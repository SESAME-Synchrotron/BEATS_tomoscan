""" Tomography scanning tool for BEATS @SESAME 
The source of this code is the derived class for 
tomography step scanning with EPICS at BEATS beamline

Notes: 

Action List: 
1. To adapt BEATS shutter in the future, currently virtual shutter is being used. 
2. To adapt motion system in the future, currently motorSim is being used.

   Classes
   -------
    TomoScanBEATSPcoMicosStep 
     
"""
import time
import os
import h5py 
import sys
import traceback
import numpy as np
from epics import PV
import threading
import re 
import json
import shutil

import socket
from datetime import timedelta
from tomoscan import data_management as dm
from tomoscan.tomoscan_step import TomoScanSTEP
from tomoscan import log
from SEDSS.CLIMessage import CLIMessage
from SEDSS.UIMessage import UIMessage
from SEDSS.SEDSupport import fileName


EPSILON = .001


class SampleXError(Exception):
    '''Exception raised when SampleX is not equal to SampleInX
    '''

class TomoScanBEATSPcoMicosStep(TomoScanSTEP):
    """Derived class used for tomography scanning with EPICS for BEATS 

    Parameters
    ----------
    pv_files : list of str
        List of files containing EPICS pvNames to be used.
    macros : dict
        Dictionary of macro definitions to be substituted when
        reading the pv_files
    """

    def __init__(self, configFile, pv_files, macros):
        super().__init__(pv_files, macros)

        self.configFile = configFile
        # read json pvlist (hard coded PVs)        
        file = open(configFile)
        self.pvlist = json.load(file)
        self.systemInitializations()      
        log.setup_custom_logger("./tomoscan.log")
    
    def systemInitializations(self):
        # set TomoScan xml files        
        self.epics_pvs['CamNDAttributesFile'].put(self.pvlist['XMLFiles']['detectorAttributes']['PcoMicosStepAttr'])
        self.epics_pvs['FPXMLFileName'].put(self.pvlist['XMLFiles']['layout']['PcoMicosStepLayout'])

        # Enable auto-increment on file writer
        self.epics_pvs['FPAutoIncrement'].put('Yes')

        # Set standard file template on file writer
        self.epics_pvs['FPFileTemplate'].put("%s%s_%3.3d.h5", wait=True)

        PV(self.pvlist['PVs']['ZMQPVs']['PcoZMQ']).put(1)

        # Disable over writing warning
        self.epics_pvs['OverwriteWarning'].put('Yes')   

    def open_shutter(self):
        """Opens the combined stopper shutter to collect flat fields or projections.

        This does the following:

        - Opens the combined stopper shutter.
        """
        if self.epics_pvs['Testing'].get():
            log.warning('In testing mode, so not opening shutters.')
        else: 
            if not self.epics_pvs['OpenShutter'] is None:
                pv = self.epics_pvs['OpenShutter']
                value = self.epics_pvs['OpenShutterValue'].get(as_string=True)
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('combined stopper shutter status: %s', status)
                log.info('open combined stopper shutter: %s, value: %s', pv, value)
                self.epics_pvs['OpenShutter'].put(value, wait=True)
                self.wait_combined_stopper_shutter_open()
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('combined stopper shutter status: %s', status)

    def close_shutter(self):
        """Closes the combined stopper shutter to collect dark fields.
        
        This does the following:

        - Closes the combined stopper shutter.
        """
        if self.epics_pvs['Testing'].get():
            log.warning('In testing mode, so not opening shutters.')
        else: 
            if not self.epics_pvs['CloseShutter'] is None:
                pv = self.epics_pvs['CloseShutter']
                value = self.epics_pvs['CloseShutterValue'].get(as_string=True)
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('combined stopper shutter status: %s', status)
                log.info('close combined stopper shutter: %s, value: %s', pv, value)
                self.epics_pvs['CloseShutter'].put(value, wait=True)
                self.wait_combined_stopper_shutter_close()
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('combined stopper shutter status: %s', status)

    def step_scan(self):
        """Control of Sample X position
        """
        if(abs(self.epics_pvs['SampleInX'].value-self.epics_pvs['SampleX'].value)>1e-4) or abs(self.epics_pvs['SampleInY'].value-self.epics_pvs['SampleY'].value)>1e-4:
            log.error('SampleInX/SampleInZ is not the same as current SampleTopX/SampleTopZ')            
            self.epics_pvs['ScanStatus'].put('Sample position error')
            self.epics_pvs['StartScan'].put(0)        
            return
        super().step_scan()

    def set_trigger_mode(self, trigger_mode, num_images):
        """ Sets PCO trigger mode

        Parameters
        ----------
        trigger_mode : str
            Choices are: "FreeRun", "Internal","Software", or "External"

        num_images : int
            Number of images to collect.  Ignored if trigger_mode="FreeRun".
            This is used to set the ``NumImages`` PV of the camera.
        """

        self.epics_pvs['CamAcquire'].put('Done') ###
        self.wait_pv(self.epics_pvs['CamAcquire'], 0) ###
        log.info('set trigger mode: %s', trigger_mode)

        if trigger_mode == 'FreeRun':
            self.epics_pvs['CamImageMode'].put('Continuous', wait=True)
            self.epics_pvs['CamTriggerMode'].put(0, wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 0)

        elif trigger_mode == 'Internal':
            self.epics_pvs['CamTriggerMode'].put(0, wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 0)
            self.epics_pvs['CamImageMode'].put('Multiple')            
            self.epics_pvs['CamNumImages'].put(num_images, wait=True)

        elif trigger_mode == 'Software':
            self.epics_pvs['CamTriggerMode'].put(0, wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 1)
            self.epics_pvs['CamTriggerSource'].put('Software', wait=True)
            self.epics_pvs['CamImageMode'].put('Multiple')            
            self.epics_pvs['CamNumImages'].put(num_images, wait=True)

        else: # set camera to external triggering
            # These are just in case the scan aborted with the camera in another state 
            self.epics_pvs['CamTriggerMode'].put(4, wait=True)     # VN: For PG we need to switch to On to be able to switch to readout overlap mode                                                              
            self.epics_pvs['CamImageMode'].put('Multiple')            
            self.epics_pvs['CamNumImages'].put(self.num_angles, wait=True)
            self.prepareTriggeringSource()
    
    def prepareTriggeringSource (self):
        # PV("FG:SetFunctionCH1").put("SQU") # square function 
        # PV("FG:SetWaveformPeriodCH1").put(0.02) # waveform period
        # PV("FG:SetBurstPeriodCH1").put(0.021) # Burst period. 
        # PV("FG:SetSquareDutyCycleCH1").put(10) # duty cycle 10%
        # PV("FG:SetBurst1").put(1) # enable burst 
        # PV("FG:SetSquareAmplitudeCH1").put(5) # 5 volt 
        # PV("FG:SetSquareOffsetCH1").put(2.5) # offset 2.5 volt, signal 0 - 5 volt on, off
        # PV("FG:SetBurstTrigSourceCH1").put(0) # manual trigger source 
        # PV("FG:SetBurstIdleCH1").put(3) # Bottom 
        # PV("FG:SetOutputStateCH1").put(1) # enable output.
        self.IP = self.pvlist['RPTrigServ']['IP']
        self.PORT = self.pvlist['RPTrigServ']['PORT']
        
    def initSEDPathFile(self): 
        """
        This method is used to set the experimental file name in compliance 
        with SESAME Experimental Data (SED) Writer (SEDW)
        """
        # =================== SED file name and path section ==========================
        
        SEDPathPV = self.pvlist['PVs']['writerSuppPVs']['SEDPath']
        SEDFileNamePV = self.pvlist['PVs']['writerSuppPVs']['SEDFileName']
        SEDTimeStampPV = self.pvlist['PVs']['writerSuppPVs']['SEDTimeStamp']
        
        PV(SEDTimeStampPV).put(self.SEDTimeStamp, wait=True)
        PV(SEDFileNamePV).put(self.SEDFileName, wait=True)
        PV(SEDPathPV).put(self.SEDPath, wait=True)

        self.epics_pvs['FilePath'].put(self.SEDPath, wait=True)
        #==============================================================================

    def begin_scan(self):
        """Performs the operations needed at the very start of a scan.

        This does the following:
        - Set data directory.
        - Set the TomoScan xml files
        - Calls the base class method.
        - Opens the front-end shutter.
        - Turns on data capture.
        """
        self.systemInitializations()
        # Check SED file name regex        
        repeats = 0
        while fileName.SED_h5re(self.epics_pvs["FileName"].get(as_string=True)): 
            if repeats == 0: 
                # UIMessage("File Name","The file name is not valid","The file directory is auto generated, please insert the file name without (spaces, extensions, and special characters except dashes)").showWarning()
                log.error("SED file name is not valid")
                self.epics_pvs['ScanStatus'].put('spaces, extensions, paths, and special characters except dashes are not allowed)')
                repeats = 1
            CLIMessage("The file directory is auto generated, please insert the file name without (spaces, extensions, and special characters except dashes)", "IR")
            time.sleep(0.5) # checks every .5 second 

        self.SEDBasePath = self.pvlist['paths']['SEDBasePath'] # this path should be in compliance with the path in SEDW
        self.SEDPath, self.SEDFileName, self.SEDTimeStamp = fileName.SED_fileName(self.SEDBasePath, self.epics_pvs["FileName"].get(as_string=True), "BEATS") 
            
        self.control_pvs['RotationHLM'].put(99999, wait = True)
        self.control_pvs['RotationLLM'].put(-99999, wait = True)  

        log.info('begin scan')
        self.initSEDPathFile()
        # Call the base class method
        super().begin_scan()

        # Write h5 file by SED writer.
        PV(self.pvlist['PVs']['writerSuppPVs']['writerImagesNumCaptured']).put(self.total_images)
        
        self.writerCheck()

        if not self.epics_pvs['UseExposureShutter'].get():
            self.epics_pvs['ExposureShutter'].put(1, wait=True)
            log.info('Exposure shutter not used')
            log.info('open exposure shutter')

    def writerCheck(self): 
        repeat = 0
        while PV(self.pvlist['PVs']['writerSuppPVs']['writerStatus']).get() != 1: 
            if repeat == 0: 
                log.error("BEATS Writer is not running!!!")
                self.epics_pvs['ScanStatus'].put('BEATS Writer is not running!!!')
                repeat = 1
            CLIMessage("BEATS Writer is not running!! Start the writer server to continue the scan AUTOMATICALLY", "IR")
            time.sleep(0.5) # checks every .5 second 
        
        repeat = 0
        while PV(self.pvlist['PVs']['writerSuppPVs']['writerFileTrigger']).get() != 0: 
            if repeat == 0: 
                log.warning("Waiting for BEATS writer | there is a file begin written by the writer")
                self.epics_pvs['ScanStatus'].put('Waiting for BEATS writer')
                repeat = 1
            CLIMessage("BEATS Writer is busey writing a file. The scan will continue AUTOMATICALLY when the writer is ready again", "IO")
            time.sleep(0.5)
    
        # Triggers the writer to generate the file and be ready for ZMQ 
        PV(self.pvlist['PVs']['writerSuppPVs']['writerFileTrigger']).put(1) 
        
        repeat = 0 
        while PV(self.pvlist['PVs']['writerSuppPVs']['writerFileCreated']).get() != 1:
            if repeat == 0: 
                log.info("Wating for BEATS Writer to prepare the H5 dxFile.") 
                self.epics_pvs['ScanStatus'].put('Creating H5 dxFile')
                repeat = 1
            CLIMessage("BEATS Writer | Wating for H5 dxFile creation", "IO")
            time.sleep(0.5)

        time.sleep(0.5)
        print ("\n")

    def update_status(self, start_time):
        """
        When called updates ``ImagesCollected``, ``ImagesSaved``, ``ElapsedTime``, and ``RemainingTime``. 

        Parameters
        ----------
        start_time : time

            Start time to calculate elapsed time.

        Returns
        -------
        elapsed_time : float

            Elapsed time to be used for time out.
        """
        num_collected  = self.epics_pvs['CamNumImagesCounter'].value
        num_images     = self.epics_pvs['CamNumImages'].value
        num_saved      = PV(self.pvlist['PVs']['writerSuppPVs']['imagesNumSaved']).get()
        num_to_save     = self.total_images
        current_time = time.time()
        elapsed_time = current_time - start_time
        remaining_time = (elapsed_time * (num_images - num_collected) /
                          max(float(num_collected), 1))
        collect_progress = str(num_collected) + '/' + str(num_images)
        log.info('Collected %s', collect_progress)
        self.epics_pvs['ImagesCollected'].put(collect_progress)
        save_progress = str(num_saved) + '/' + str(num_to_save)
        log.info('Saved %s', save_progress)
        self.epics_pvs['ImagesSaved'].put(save_progress)
        self.epics_pvs['ElapsedTime'].put(str(timedelta(seconds=int(elapsed_time))))
        self.epics_pvs['RemainingTime'].put(str(timedelta(seconds=int(remaining_time))))

        return elapsed_time

    def end_scan(self):
        """Performs the operations needed at the very end of a scan.

        This does the following:
        - Reset rotation position by mod 360.
        - Calls the base class method.
        - Closes shutter.  
        - Copy raw data to data analysis computer.      
        """

        if not self.epics_pvs['UseExposureShutter'].get():
            self.epics_pvs['ExposureShutter'].put(0, wait=True)
            log.info('close exposure shutter')


        if self.return_rotation == 'Yes':
            # Reset rotation position by mod 360 , the actual return 
            # to start position is handled by super().end_scan()
            log.info('wait until the stage is stopped')
            time.sleep(self.epics_pvs['RotationAccelTime'].get()*1.2)                        
            ang = self.epics_pvs['RotationRBV'].get()
            current_angle = np.sign(ang)*(np.abs(ang)%360)
            self.epics_pvs['RotationSet'].put('Set', wait=True)
            self.epics_pvs['Rotation'].put(current_angle, wait=True)
            self.epics_pvs['RotationSet'].put('Use', wait=True)

        log.info('end scan')
        # Save the configuration
        # Strip the extension from the FullFileName and add .config
        full_file_name = self.SEDPath + "/" + self.SEDFileName
        log.info('data save location: %s', full_file_name)
        config_file_root = os.path.splitext(full_file_name)[0]
        self.save_configuration(config_file_root + '.config')

        # Call the base class method
        super().end_scan()
        # Close shutter
        self.close_shutter()

    def save_configuration(self, file_name):
        """Saves the current configuration PVs to a file.

        A new dictionary is created, containing the key for each PV in the ``config_pvs`` dictionary
        and the current value of that PV.  This dictionary is written to the file in JSON format.
        """
        config = {}
        for key in self.config_pvs:
            config[key] = self.config_pvs[key].get(as_string=True)
        try:
            out_file = f = open(self.SEDBasePath + "/config.config", mode='w', encoding='utf-8')
            json.dump(config, out_file, indent=2)
            out_file.close()
            time.sleep(.1)
            shutil.move (self.SEDBasePath + "/config.config", file_name)

        except (PermissionError, FileNotFoundError) as error:
            log.error('Error writing configuration file')
            self.epics_pvs['ScanStatus'].put('Error writing configuration')

    def wait_pv(self, epics_pv, wait_val, timeout=-1):
        """Wait on a pv to be a value until max_timeout (default forever)
           delay for pv to change
        """

        time.sleep(.01)
        start_time = time.time()
        while True:
            pv_val = epics_pv.get()
            if isinstance(pv_val, float):
                if abs(pv_val - wait_val) < EPSILON:
                    return True
            if pv_val != wait_val:
                if timeout > -1:
                    current_time = time.time()
                    diff_time = current_time - start_time
                    if diff_time >= timeout:
                        log.error('  *** ERROR: DROPPED IMAGES ***')
                        log.error('  *** wait_pv(%s, %d, %5.2f reached max timeout. Return False',
                                      epics_pv.pvname, wait_val, timeout)
                        return False
                time.sleep(.01)
            else:
                return True
 
    def wait_combined_stopper_shutter_open(self, timeout=-1):
        """Waits for the combined stopper shutter to open, or for ``abort_scan()`` to be called.

        While waiting this method periodically tries to open the shutter..

        Parameters
        ----------
        timeout : float
            The maximum number of seconds to wait before raising a ShutterTimeoutError exception.

        Raises
        ------
        ScanAbortError
            If ``abort_scan()`` is called
        ShutterTimeoutError
            If the open shutter has not completed within timeout value.
        """

        start_time = time.time()
        pv = self.epics_pvs['OpenShutter']
        value = self.epics_pvs['OpenShutterStatusValue'].get(as_string = True)
        log.info('open shutter: %s, value: %s', pv, value)
        elapsed_time = 0
        while True:
            if self.epics_pvs['ShutterStatus'].get() == int(value):
                log.warning("Shutter is open in %f s", elapsed_time)
                return
            if not self.scan_is_running:
                exit()
            value = self.epics_pvs['OpenShutterStatusValue'].get()
            time.sleep(1.0)
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.warning("Waiting on shutter to open: %f s", elapsed_time)
            # self.epics_pvs['OpenShutter'].put(value, wait=True)
            if timeout > 0:
                if elapsed_time >= timeout:
                   exit()

    def collect_projections(self):
            """
            This does the following:
            - Call the superclass collect_projections() function.
            - Set the trigger mode on the camera.
            - Set the camera in acquire mode.
            - Starts the camera acquiring in software trigger mode.
            - Update scan status.
            """

            log.info('collect projections')

            self.set_trigger_mode('External', self.num_angles)
               
            # Start the camera
            self.epics_pvs['CamAcquire'].put('Acquire')
            # Need to wait a short time for AcquireBusy to change to 1
            time.sleep(2)
            self.open_shutter()
            self.epics_pvs['HDF5Location'].put(self.epics_pvs['HDF5ProjectionLocation'].value)
            self.epics_pvs['FrameType'].put('Projection')

            start_time = time.time()
            stabilization_time = self.epics_pvs['StabilizationTime'].get()
            log.info("stabilization time %f s", stabilization_time)

            if self.epics_pvs['UseExposureShutter'].get():
                for k in range(self.num_angles):
                    if(self.scan_is_running):
                        log.info('angle %d: %f', k, self.theta[k])
                        self.epics_pvs['Rotation'].put(self.theta[k], wait=True)            
                        time.sleep(stabilization_time)
                        log.info('open exposure shutter')
                        self.epics_pvs['ExposureShutter'].put(1, wait=True)
                        time.sleep(0.01)
                        # self.epics_pvs['CamTriggerSoftware'].put(1)    
                        # PV("FG:BurstTrigCH1").put(1)
                        s = socket.socket()
                        s.connect((self.IP, int(self.PORT)))
                        x=time.time()   
                        log.info('Sending trigger #%d', k)
                        s.send(str(x).encode('utf-8'))
                        time.sleep(self.epics_pvs['ExposureTime'].get())
                        self.epics_pvs['ExposureShutter'].put(0, wait=True)
                        s.close()
                        log.info('close exposure shutter')
                        self.wait_pv(self.epics_pvs['CamNumImagesCounter'], k+1, 60)
                        self.update_status(start_time)
            else:   
                for k in range(self.num_angles):
                    if(self.scan_is_running):
                        log.info('angle %d: %f', k, self.theta[k])
                        self.epics_pvs['Rotation'].put(self.theta[k], wait=True)            
                        time.sleep(stabilization_time)
                        #log.info('open exposure shutter')
                        # self.epics_pvs['ExposureShutter'].put(1, wait=True)
                        # time.sleep(0.01)
                        # self.epics_pvs['CamTriggerSoftware'].put(1)    
                        # PV("FG:BurstTrigCH1").put(1)
                        s = socket.socket()
                        s.connect((self.IP, int(self.PORT)))
                        x=time.time()   
                        log.info('Sending trigger #%d', k)
                        s.send(str(x).encode('utf-8'))
                        #time.sleep(self.epics_pvs['ExposureTime'].get())
                        # self.epics_pvs['ExposureShutter'].put(0, wait=True)
                        s.close()
                        #log.info('close exposure shutter')
                        self.wait_pv(self.epics_pvs['CamNumImagesCounter'], k+1, 60)
                        self.update_status(start_time)
            
            # wait until the last frame is saved (not needed)
            time.sleep(0.5)        
            self.update_status(start_time)

    def wait_combined_stopper_shutter_close(self, timeout=-1):
        """Waits for the combined stopper shutter to close, or for ``abort_scan()`` to be called.

        While waiting this method periodically tries to close the shutter..

        Parameters
        ----------
        timeout : float
            The maximum number of seconds to wait before raising a ShutterTimeoutError exception.

        Raises
        ------
        ScanAbortError
            If ``abort_scan()`` is called
        ShutterTimeoutError
            If the close shutter has not completed within timeout value.
        """

        start_time = time.time()
        pv = self.epics_pvs['CloseShutter']
        value = self.epics_pvs['CloseShutterStatusValue'].get(as_string = True)
        log.info('close combined stopper shutter: %s, value: %s', pv, value)
        elapsed_time = 0
        while True:
            if self.epics_pvs['ShutterStatus'].get() == int(value):
                log.warning("Shutter is close in %f s", elapsed_time)
                return
            if not self.scan_is_running:
                exit()
            value = self.epics_pvs['CloseShutterStatusValue'].get()
            time.sleep(1.0)
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.warning("Waiting on shutter to close: %f s", elapsed_time)
            # self.epics_pvs['CloseShutter'].put(value, wait=True)
            if timeout > 0:
                if elapsed_time >= timeout:
                   exit()