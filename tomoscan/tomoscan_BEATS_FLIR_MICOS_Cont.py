"""Tomography scanning tool for BEATS @SESAME 
The source of this code is the derived class for 
tomography continuous scanning with EPICS at BEATS beamline 

Notes: 

Action List: 
1. To adapt BEATS shutter in the future, currently virtual shutter is being used. 
2. To adapt motion system in the future, currently motorSim is being used.

   Classes
   -------
    TomoScanBEATSFlirMicosCont 
"""
import time
import os
import sys
import h5py 
import traceback
import numpy as np
import math
from epics import PV
import threading
import re 
import json
import shutil

from datetime import timedelta
from tomoscan import data_management as dm
from tomoscan import TomoScanCont
from tomoscan import log
from SEDSS.SEDSupplements import CLIMessage, UIMessage
from SEDSS.SEDSupport import fileName


EPSILON = .001

class TomoScanBEATSFlirMicosCont(TomoScanCont):
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

        # read json pvlist (hard coded PVs)        
        file = open("/opt/SW/venv3.9/lib/python3.9/site-packages/tomoscan-0.1-py3.9.egg/configurations/pvlist.json")
        self.pvlist = json.load(file)

        # set BEATS TomoScan xml files
        self.epics_pvs['CamNDAttributesFile'].put(self.pvlist['XMLFiles']['detectorAttributes']['FlirMicosContAttr'])
        self.epics_pvs['FPXMLFileName'].put(self.pvlist['XMLFiles']['layout']['FlirMicosContLayout'])
        self.control_pvs['CamExposureAuto'].put(0) # set exposure auto off
        self.control_pvs['CamFrameRateEnable'].put(0) # set frame rate enable to No

        # Enable auto-increment on file writer
        self.epics_pvs['FPAutoIncrement'].put('Yes')

        # Set standard file template on file writer
        self.epics_pvs['FPFileTemplate'].put("%s%s_%3.3d.h5", wait=True)

        PV(self.pvlist['PVs']['ZMQPVs']['FlirZMQ']).put(1)

        # Disable over writing warning
        self.epics_pvs['OverwriteWarning'].put('Yes')
        log.setup_custom_logger("./tomoscan.log")

    def open_frontend_shutter(self):
        """Opens the shutters to collect flat fields or projections.

        This does the following:

        - Checks if we are in testing mode. If we are, do nothing else opens the front-end shutter.

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
            # Close front-end shutter
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

        if not self.epics_pvs['CloseFastShutter'] is None:
            pv = self.epics_pvs['CloseFastShutter']
            value = self.epics_pvs['CloseFastShutterValue'].get(as_string=True)
            log.info('close fast shutter: %s, value: %s', pv, value)
            self.epics_pvs['CloseFastShutter'].put(value, wait=True)
    
    def set_trigger_mode(self, trigger_mode, num_images):
        """ Sets FLIR trigger mode

        Parameters
        ----------
        trigger_mode : str
            Choices are: "FreeRun", "Internal", or "Software"

        num_images : int
            Number of images to collect.  Ignored if trigger_mode="FreeRun".
            This is used to set the ``NumImages`` PV of the camera.
        """

        self.epics_pvs['CamAcquire'].put('Done') 
        self.wait_pv(self.epics_pvs['CamAcquire'], 0)
        log.info('set trigger mode: %s', trigger_mode)

        if trigger_mode == 'FreeRun':
            self.epics_pvs['CamImageMode'].put('Continuous', wait=True)
            self.epics_pvs['CamTriggerMode'].put('Off', wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 0)

        elif trigger_mode == 'Internal':
            self.epics_pvs['CamTriggerMode'].put('Off', wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 0)
            self.epics_pvs['CamImageMode'].put('Multiple')            
            self.epics_pvs['CamNumImages'].put(num_images, wait=True)

        elif trigger_mode == 'Software':
            self.epics_pvs['CamTriggerMode'].put('On', wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 1)
            self.epics_pvs['CamTriggerSource'].put('Software', wait=True)
            self.epics_pvs['CamImageMode'].put('Multiple')            
            self.epics_pvs['CamNumImages'].put(num_images, wait=True)
    
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
        """

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

        """
        FLIR Oryx ORX-10G-71S7M camera or its driver does not support capturing one frame with continuous 
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
        self.initSEDPathFile()
        # Call the base class method
        super().begin_scan()
        
        # Write h5 file by SED writer.
        PV(self.pvlist['PVs']['writerSuppPVs']['writerImagesNumCaptured']).put(self.total_images)

        self.writerCheck()
        # Opens the front-end shutter
        self.open_frontend_shutter()    

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

        if self.return_rotation == 'Yes':
            # Reset rotation position by mod 360 , the actual return 
            # to start position is handled by super().end_scan()
            log.info('wait until the stage is stopped')
            time.sleep(3)                        
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

        super().end_scan()
  
        self.close_shutter()
        self.control_pvs['RotationStop'].put(1) # stops the motor. 

    # adding theta to the experimental file is managed by SEDW

    def save_configuration(self, file_name):
        """Saves the current configuration PVs to a file.

        A new dictionary is created, containing the key for each PV in the ``config_pvs`` dictionary
        and the current value of that PV.  This dictionary is written to the file in JSON format.

        Parameters
        ----------
        file_name : str
            The name of the file to save to.
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