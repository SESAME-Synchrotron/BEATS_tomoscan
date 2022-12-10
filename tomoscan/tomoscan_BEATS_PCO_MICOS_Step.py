""" Tomography scanning tool for BEATS @SESAME 
The source of this code is the derived class for 
tomography step scanning with EPICS at APS beamline 32-ID


   Classes
   -------
   TomoScanBEATS
     
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

from datetime import timedelta
from tomoscan import data_management as dm
from tomoscan.tomoscan_step import TomoScanSTEP
from tomoscan import log
from SEDSS.SEDSupplements import CLIMessage, CLIInputReq 


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

    def __init__(self, pv_files, macros):
        super().__init__(pv_files, macros)

        # set TomoScan xml files        
        self.epics_pvs['CamNDAttributesFile'].put('ADZMQ_BEATS_PCO_MICOS_Step_DetectorAttributes.xml')
        self.epics_pvs['FPXMLFileName'].put('ADZMQ_BEATS_PCO_MICOS_Step_Layout.xml')

        #macro = 'DET=' + self.pv_prefixes['Camera'] + ',' + 'TS=' + self.epics_pvs['Testing'].__dict__['pvname'].replace('Testing', '', 1)
        #self.control_pvs['CamNDAttributesMacros'].put(macro)

        # Enable auto-increment on file writer
        self.epics_pvs['FPAutoIncrement'].put('Yes')

        # Set standard file template on file writer
        self.epics_pvs['FPFileTemplate'].put("%s%s_%3.3d.h5", wait=True)

        # Disable over writing warning
        self.epics_pvs['OverwriteWarning'].put('Yes')    

        # # TXMOptics
        # txmoptics_prefix = '32id:TXMOptics:'
        # self.epics_pvs['TXMEnergySet'] = PV(txmoptics_prefix+'EnergySet')
        # self.epics_pvs['TXMEnergy'] = PV(txmoptics_prefix+'Energy')
        # self.epics_pvs['TXMMoveAllOut'] = PV(txmoptics_prefix+'MoveAllOut')
        # self.epics_pvs['TXMMoveAllIn'] = PV(txmoptics_prefix+'MoveAllIn')  

        # # energy scan
        # self.epics_pvs['EnergySet'].put(0)
        # self.epics_pvs['EnergySet'].add_callback(self.pv_callback_32id)

        log.setup_custom_logger("./tomoscan.log")
    
    
    def open_frontend_shutter(self):
        """Opens the shutters to collect flat fields or projections.

        This does the following:

        - Checks if we are in testing mode. If we are, do nothing else opens the 2-BM-A front-end shutter.

        """
        if self.epics_pvs['Testing'].get():
            log.warning('In testing mode, so not opening shutters.')
        else:
            # Open front-end shutter
            if not self.epics_pvs['OpenShutter'] is None:
                pv = self.epics_pvs['OpenShutter']
                value = self.epics_pvs['OpenShutterValue'].get(as_string=True)
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('shutter status: %s', status)
                log.info('open shutter: %s, value: %s', pv, value)
                self.epics_pvs['OpenShutter'].put(value, wait=True)
                self.wait_frontend_shutter_open()
                # self.wait_pv(self.epics_pvs['ShutterStatus'], 1)
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('shutter status: %s', status)

    def open_shutter(self):
        """Opens the shutters to collect flat fields or projections.

        This does the following:

        - Opens the fast shutter.
        """

        # Open 32-ID-C fast shutter
        if not self.epics_pvs['OpenFastShutter'] is None:
            pv = self.epics_pvs['OpenFastShutter']
            value = self.epics_pvs['OpenFastShutterValue'].get(as_string=True)
            log.info('open fast shutter: %s, value: %s', pv, value)
            self.epics_pvs['OpenFastShutter'].put(value, wait=True)

    def close_frontend_shutter(self):
        """Closes the shutters to collect dark fields.
        This does the following:

        - Closes the front-end shutter.

        """
        if self.epics_pvs['Testing'].get():
            log.warning('In testing mode, so not opening shutters.')
        else:
            # Close the front-end shutter
            if not self.epics_pvs['CloseShutter'] is None:
                pv = self.epics_pvs['CloseShutter']
                value = self.epics_pvs['CloseShutterValue'].get(as_string=True)
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('shutter status: %s', status)
                log.info('close shutter: %s, value: %s', pv, value)
                self.epics_pvs['CloseShutter'].put(value, wait=True)
                self.wait_pv(self.epics_pvs['ShutterStatus'], 0)
                status = self.epics_pvs['ShutterStatus'].get(as_string=True)
                log.info('shutter status: %s', status)

    def close_shutter(self):
        """Closes the shutters to collect dark fields.
        This does the following:

        - Closes the fast shutter.
        """

        # Close fast shutter
        if not self.epics_pvs['CloseFastShutter'] is None:
            pv = self.epics_pvs['CloseFastShutter']
            value = self.epics_pvs['CloseFastShutterValue'].get(as_string=True)
            log.info('close fast shutter: %s, value: %s', pv, value)
            self.epics_pvs['CloseFastShutter'].put(value, wait=True)

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
        """Sets the trigger mode SIS3820 and the camera.

        Parameters
        ----------
        trigger_mode : str
            Choices are: "FreeRun", "Internal", or "PSOExternal"

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
            # self.epics_pvs['CamAcquire'].put('Acquire')

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
            self.epics_pvs['CamTriggerMode'].put(4, wait=True)
            #self.wait_pv(self.epics_pvs['CamTriggerMode'], 1)
            self.prepareTriggeringSource()
    
    def prepareTriggeringSource (self):
        PV("FG:SetFunctionCH1").put("SQU") # square function 
        PV("FG:SetWaveformPeriodCH1").put(0.02) # waveform period
        PV("FG:SetBurstPeriodCH1").put(0.021) # Burst period. 
        PV("FG:SetSquareDutyCycleCH1").put(10) # duty cycle 10%
        PV("FG:SetBurst1").put(1) # enable burst 
        PV("FG:SetSquareAmplitudeCH1").put(5) # 5 volt 
        PV("FG:SetSquareOffsetCH1").put(2.5) # offset 2.5 volt, signal 0 - 5 volt on, off
        PV("FG:SetBurstTrigSourceCH1").put(0) # manual trigger source 
        PV("FG:SetBurstIdleCH1").put(3) # Bottom 
        PV("FG:SetOutputStateCH1").put(1) # enable output.
        

    def initSEDPathFile(self): 
        """
        This method is used to set the experimintal file name in compliance 
        with SESAME Experimintal Data (SED) Writer (SEDW)
        """
        # =================== SED file name and path section ==========================

        self.SEDBasePath = "/home/hdfData" # this path should be in compliance with the path in SEDW
        
        SEDPathPV = "BEATS:SEDPath"
        SEDFileNamePV = "BEATS:SEDFileName"
        SEDTimeStampPV = "BEATS:SEDTimeStamp"

        self.SEDTimeStamp = str(time.strftime("%Y%m%dT%H%M%S"))

        self.SEDFileName = self.epics_pvs["FileName"].get(as_string=True)
        if not re.match(r'\S', self.SEDFileName): #To check a line whether it starts with a non-space character or not.
            self.SEDFileName = "BEATS"
        self.SEDFileName = self.SEDFileName + "-" + self.SEDTimeStamp
        self.SEDPath = self.SEDBasePath + "/" + self.SEDFileName
        
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
        """
        FLIR Oryx ORX-10G-71S7M camera or its driver does not support capturing one fram with continous 
        trigger mode. this makes the SEDWritter unstaible as it needs to know how many frames are going to 
        be recevied.... however that's why this part of the code has been added. 
        """
        if  self.epics_pvs['NumAngles'].get() == 1: 
            self.epics_pvs['NumAngles'].put(2, wait=True)
            log.info("replace number of angles to 2 instead of 1")
        
        if self.epics_pvs['NumDarkFields'].get() == 1:
            self.epics_pvs['NumDarkFields'].put(2)
            log.info("replace number of dark fields to 2 instead of 1")

        if self.epics_pvs['NumFlatFields'].get() == 1: 
            self.epics_pvs['NumFlatFields'].put(2)
            log.info("replace number of flat fields to 2 instead of 1")
            
        self.control_pvs['RotationHLM'].put(99999, wait = True)
        self.control_pvs['RotationLLM'].put(-99999, wait = True)

            

        log.info('begin scan')
        #self.update_status()
        self.initSEDPathFile()

        # Set data directory
        # file_path = self.epics_pvs['DetectorTopDir'].get(as_string=True) + self.epics_pvs['ExperimentYearMonth'].get(as_string=True) + os.path.sep + self.epics_pvs['UserLastName'].get(as_string=True) + os.path.sep
        file_path = "/home/hdfData/"

        self.epics_pvs['FilePath'].put(file_path, wait=True)

        # Call the base class method
        super().begin_scan()
        self.writerCheck()
        # Opens the front-end shutter
        self.open_frontend_shutter()
    
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
        num_saved      = PV("BEATS:WRITER:NumSaved").get()
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

    def writerCheck(self): 
        repeat = 0
        while PV("BEATS:WRITER:Status").get() != 1: 
            if repeat == 0: 
                #print("\n")
                log.error("BEATS Writer is not running!!!")
                repeat = 1
            CLIMessage("BEATS Writer is not running!! Start the writer server to continue the scan AUTOMATICALLY", "IR")
            time.sleep(0.5) # checks every .5 second 
        
        repeat = 0
        while PV("BEATS:WRITER:NewFileTrigger").get() != 0: 
            if repeat == 0: 
                log.warning("Waiting for BEATS writer | there is a file begin written by the writer")
                repeat = 1
            CLIMessage("BEATS Writer is busey writing a file. The scan will continue AUTOMATICALLY when the writer is ready again", "IO")
            time.sleep(0.5)
    
        #Triggers the writer to generat the file and be ready for ZMQ 
        PV("BEATS:WRITER:NewFileTrigger").put(1) 
        
        repeat = 0 
        while PV("BEATS:WRITER:FileCreated").get() != 1:
            if repeat == 0: 
                log.info("Wating for BEATS Writer to preapre the H5 dxFile.") 
                repeat = 1
            CLIMessage("BEATS Writer | Wating for H5 dxFile creation", "IO")
            time.sleep(0.5)

        time.sleep(0.5)

    def end_scan(self):
        """Performs the operations needed at the very end of a scan.

        This does the following:

        - Reset rotation position by mod 360.

        - Calls the base class method.

        - Closes shutter.  

        - Add theta to the raw data file. 

        - Copy raw data to data analysis computer.      
        """

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

        # Call the base class method
        super().end_scan()
        # Close shutter
        self.close_shutter()

        # Stop the file plugin
        #self.epics_pvs['FPCapture'].put('Done')
        #self.wait_pv(self.epics_pvs['FPCaptureRBV'], 0)
        # Add theta in the hdf file
        # self.add_theta()

    def save_configuration(self, file_name):
        """Saves the current configuration PVs to a file.

        A new dictionary is created, containing the key for each PV in the ``config_pvs`` dictionary
        and the current value of that PV.  This dictionary is written to the file in JSON format.
        """
        file_name = self.SEDPath + "/" + self.SEDFileName + ".config"

        config = {}
        for key in self.config_pvs:
            config[key] = self.config_pvs[key].get(as_string=True)
        try:
            out_file = f = open("/home/hdfData/config.config", mode='w', encoding='utf-8')
            json.dump(config, out_file, indent=2)
            out_file.close()
            time.sleep(.1)
            shutil.move ("/home/hdfData/config.config", file_name)
        except (PermissionError, FileNotFoundError) as error:
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
 
    def wait_frontend_shutter_open(self, timeout=-1):
        """Waits for the front end shutter to open, or for ``abort_scan()`` to be called.

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
        value = self.epics_pvs['OpenShutterValue'].get(as_string = True)
        log.info('open shutter: %s, value: %s', pv, value)
        elapsed_time = 0
        while True:
            if self.epics_pvs['ShutterStatus'].get() == int(value):
                log.warning("Shutter is open in %f s", elapsed_time)
                return
            if not self.scan_is_running:
                exit()
            value = self.epics_pvs['OpenShutterValue'].get()
            time.sleep(1.0)
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.warning("Waiting on shutter to open: %f s", elapsed_time)
            self.epics_pvs['OpenShutter'].put(value, wait=True)
            if timeout > 0:
                if elapsed_time >= timeout:
                   exit()


    def collect_projections(self):
            """Collects projections in fly scan mode.

            This does the following:

            - Call the superclass collect_projections() function.

            - Set the trigger mode on the camera.
       
            - Set the camera in acquire mode.

            - Starts the camera acquiring in software trigger mode.

            - Update scan status.
            """

            log.info('collect projections')
            #super().collect_projections()

            self.set_trigger_mode('External', self.num_angles)
               
            # Start the camera
            self.epics_pvs['CamAcquire'].put('Acquire')
            # Need to wait a short time for AcquireBusy to change to 1
            time.sleep(2)
            self.epics_pvs['HDF5Location'].put(self.epics_pvs['HDF5ProjectionLocation'].value)
            self.epics_pvs['FrameType'].put('Projection')

            start_time = time.time()
            stabilization_time = self.epics_pvs['StabilizationTime'].get()
            log.info("stabilization time %f s", stabilization_time)
            for k in range(self.num_angles):
                if(self.scan_is_running):
                    log.info('angle %d: %f', k, self.theta[k])
                    self.epics_pvs['Rotation'].put(self.theta[k], wait=True)            
                    time.sleep(stabilization_time)
                    #self.epics_pvs['CamTriggerSoftware'].put(1)    
                    PV("FG:BurstTrigCH1").put(1)
                    self.wait_pv(self.epics_pvs['CamNumImagesCounter'], k+1, 60)
                    self.update_status(start_time)
            
            # wait until the last frame is saved (not needed)
            time.sleep(0.5)        
            self.update_status(start_time)                