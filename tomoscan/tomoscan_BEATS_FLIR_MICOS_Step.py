"""
Tomography scanning tool for BEATS @SESAME
The source of this code is the derived class for
tomography step scanning with EPICS at BEATS beamline
"""

"""
   Classes
   -------
    TomoScanBEATSFlirMicosStep
"""
import time
from datetime import timedelta
import os
import sys
import json
import shutil
import subprocess
from epics import PV

from tomoscan.tomoscan_step import TomoScanSTEP
from tomoscan import log

from SEDSS.CLIMessage import CLIMessage
from SEDSS.UIMessage import UIMessage
from SEDSS.SEDSupport import fileName
from SEDSS.SEDFileManager import readFile, path
from SEDSS.SEDValueValidate import CSVProposal


EPSILON = .001

class TomoScanBEATSFlirMicosStep(TomoScanSTEP):
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
        log.setup_custom_logger('./tomoscan.log')

    def systemInitializations(self):
        # set TomoScan xml files
        self.epics_pvs['CamNDAttributesFile'].put(self.pvlist['XMLFiles']['detectorAttributes']['FlirMicosStepAttr'])
        self.epics_pvs['FPXMLFileName'].put(self.pvlist['XMLFiles']['layout']['FlirMicosStepLayout'])
        self.control_pvs['CamExposureAuto'].put(0) # set exposure auto off
        self.control_pvs['CamFrameRateEnable'].put(0) # set frame rate enable to No

        # Enable auto-increment on file writer
        self.epics_pvs['FPAutoIncrement'].put('Yes')

        # Set standard file template on file writer
        self.epics_pvs['FPFileTemplate'].put('%s%s_%3.3d.h5', wait=True)

        PV(self.pvlist['PVs']['ZMQPVs']['FlirZMQ']).put(1, wait=True)

        # Disable over writing warning
        self.epics_pvs['OverwriteWarning'].put('Yes')

        # Disable unused plugins
       #PV(self.pvlist['PVs']['TransPVs']['FLIR']['enablePlugin']).put(0, wait=True)
        PV(self.pvlist['PVs']['NexusPVs']['FLIR']['enablePlugin']).put(0, wait=True)

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
        """
        Control of Sample X position
        """
        if(abs(self.epics_pvs['SampleInX'].value-self.epics_pvs['SampleX'].value)>1e-4) or abs(self.epics_pvs['SampleInY'].value-self.epics_pvs['SampleY'].value)>1e-4:
            log.error('SampleInX/SampleInZ is not the same as current SampleTopX/SampleTopZ')
            self.epics_pvs['ScanStatus'].put('Sample position error')
            self.epics_pvs['StartScan'].put(0)
            return
        super().step_scan()

    def set_trigger_mode(self, trigger_mode, num_images):
        """ Sets FLIR trigger mode

        Parameters
        ----------
        trigger_mode : str
            Choices are: "FreeRun", "Internal", "Software", or "External"

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

        else: # set camera to external triggering
            # These are just in case the scan aborted with the camera in another state
            self.epics_pvs['CamTriggerMode'].put('On', wait=True)     # VN: For PG we need to switch to On to be able to switch to readout overlap mode
            self.epics_pvs['CamTriggerSource'].put('Line2', wait=True)
            self.epics_pvs['CamTriggerOverlap'].put('ReadOut', wait=True)
            self.epics_pvs['CamExposureMode'].put('Timed', wait=True)
            self.epics_pvs['CamImageMode'].put('Multiple')
            self.epics_pvs['CamArrayCallbacks'].put('Enable')
            #self.epics_pvs['CamFrameRateEnable'].put(0)
            self.epics_pvs['CamNumImages'].put(self.num_angles, wait=True)
            self.epics_pvs['CamTriggerMode'].put('On', wait=True)
            self.wait_pv(self.epics_pvs['CamTriggerMode'], 1)

    def initSEDPathFile(self):
        """
        This method is used to set the experimental file name in compliance
        with SESAME Experimental Data (SED) Writer (SEDW)
        """

        SEDPathPV = self.pvlist['PVs']['writerSuppPVs']['SEDPath']
        SEDFileNamePV = self.pvlist['PVs']['writerSuppPVs']['SEDFileName']
        SEDTimeStampPV = self.pvlist['PVs']['writerSuppPVs']['SEDTimeStamp']

        top = self.pvlist['paths']['SEDTop']
        schToday= os.path.expanduser(self.pvlist['paths']['todayProposal'])
        schProposals = os.path.expanduser(self.pvlist['paths']['schProposals'])

        self.breakFlag = 0

        while True:
            type = self.epics_pvs['ProposalTitle'].get(as_string=True).strip().upper()
            if type == 'IH':
                self.SEDPath = path(top, beamline='BEATS').getIHPath() + '/' + self.SEDFileName
                break
            elif type == 'USER':
                try:
                    proposal = int(self.epics_pvs['ProposalNumber'].get().strip())
                    if isinstance(proposal, int) and len(str(proposal)) == 8:
                        if not CSVProposal(schToday, proposal).lookup():
                            if CSVProposal(schProposals, proposal).lookup():
                                pass
                            else:
                                self.breakFlag = 1
                                break
                        self.SEDPath = path(top, beamline='BEATS', proposal=proposal, semester=readFile(schProposals).getProposalInfo(proposal, type='sem')).getPropPath() + '/' + self.SEDFileName
                        break
                    else:
                        self.epics_pvs['ScanStatus'].put(f'ProposalID:{proposal}, please enter a valid proposal number')
                        CLIMessage('please enter a valid proposal number', 'IR')
                except:
                    self.epics_pvs['ScanStatus'].put('please enter a valid proposal number')
                    CLIMessage(f'ProposalID:{proposal}, please enter a valid proposal number', 'IR')
            else:
                self.epics_pvs['ScanStatus'].put('please enter a valid experiment type, {IH, User}')
                CLIMessage('please enter a valid experiment type, {IH, User}', 'IR')
            time.sleep(0.2)

        if self.breakFlag:
            CLIMessage('Wrong proposal ID or not scheduled, Proposal ID verification', "E")
            sys.exit()

        PV(SEDTimeStampPV).put(self.SEDTimeStamp, wait=True)
        PV(SEDFileNamePV).put(self.SEDFileName, wait=True)
        PV(SEDPathPV).put(self.SEDPath, wait=True)
        self.epics_pvs['FilePath'].put(self.SEDPath, wait=True)

    def begin_scan(self):
        """Performs the operations needed at the very start of a scan.

        This does the following:
        - Set data directory.
        - Set the TomoScan xml files
        - Calls the base class method.
        - Opens the front-end shutter.
        - Turns on data capture.
        """

        repeat = 0
        while PV(self.pvlist['PVs']['writerSuppPVs']['writerWritingDone']).get() != 0: # 0 : writer is ready to start new file, 1 : not ready
            if repeat == 0:
                log.warning('Waiting writer to be ready.')
                self.epics_pvs['ScanStatus'].put('Waiting writer to be ready')
                repeat = 1
            CLIMessage('BEATS Writer | Wating to be ready', 'IG')
            time.sleep(0.1)

        scriptsPath = os.path.expanduser(self.pvlist['paths']['scripts'])
        stopCommand = [scriptsPath + 'BEATS_GUI_Bash_Stop', '--process', 'FLIR_WriterServerStep']
        startCommand = [scriptsPath + 'BEATS_GUI_Bash_Start', '--process', 'FLIR_WriterServerStep']
        xtermCommandStart = [scriptsPath + 'writer_flir_step_start.sh']
        xtermCommandStop = [scriptsPath + 'writer_flir_step_stop.sh']
        try:
            subprocess.run(xtermCommandStop)
            time.sleep(2)
            subprocess.run(stopCommand, check=True)
            subprocess.run(startCommand, check=True)
            time.sleep(1)
            subprocess.run(xtermCommandStart, check=True)
        except subprocess.CalledProcessError as e:
            CLIMessage(f'Error running the script: {e}', 'E')

        self.systemInitializations()

        # Check SED file name regex
        repeats = 0
        while fileName.SED_h5re(self.epics_pvs['FileName'].get(as_string=True)):
            if repeats == 0:
                log.error('SED file name is not valid')
                self.epics_pvs['ScanStatus'].put('spaces, extensions, paths, and special characters except dashes are not allowed)')
                repeats = 1
            CLIMessage('The file directory is auto generated, please insert the file name without (spaces, extensions, and special characters except dashes)', 'IR')
            time.sleep(0.5)

        self.SEDBasePath = self.pvlist['paths']['SEDBasePath']
        self.SEDPath, self.SEDFileName, self.SEDTimeStamp = fileName.SED_fileName(self.SEDBasePath, self.epics_pvs['FileName'].get(as_string=True), 'BEATS')

        """
        FLIR Oryx ORX-10G-71S7M camera or its driver does not support capturing one frame with continuous
        trigger mode. this makes the SEDWriter unstable as it needs to know how many frames are going to
        be received.... however that's why this part of the code has been added.
        """
        if  self.epics_pvs['NumAngles'].get() == 1:
            self.epics_pvs['NumAngles'].put(2, wait=True)
            log.info('replace number of angles to 2 instead of 1')

        if self.epics_pvs['NumDarkFields'].get() == 1:
            self.epics_pvs['NumDarkFields'].put(2)
            log.info('replace number of dark fields to 2 instead of 1')

        if self.epics_pvs['NumFlatFields'].get() == 1:
            self.epics_pvs['NumFlatFields'].put(2)
            log.info('replace number of flat fields to 2 instead of 1')

        self.control_pvs['RotationHLM'].put(99999, wait = True)
        self.control_pvs['RotationLLM'].put(-99999, wait = True)

        log.info('begin scan')
        self.initSEDPathFile()
        # Call the base class method
        super().begin_scan()

        # prepare the parameters if NDPluginProcess is being used
        if PV(self.pvlist['PVs']['PROCPVs']['FLIR']['pluginEnabled']).get() and PV(self.pvlist['PVs']['PROCPVs']['FLIR']['filterEnabled']).get() and PV(self.pvlist['PVs']['PROCPVs']['FLIR']['ZMQPort']).get(as_string=True) == "PROC1":

            PV(self.pvlist['PVs']['PROCPVs']['FLIR']['autoResetFilter']).put(1, wait=True)
            PV(self.pvlist['PVs']['PROCPVs']['FLIR']['resetFilter']).put(1, wait=True)
            self.useProcPlugin = True

            if PV(self.pvlist['PVs']['PROCPVs']['FLIR']['filterCallbacks']).get():
                self.NFilters = int(PV(self.pvlist['PVs']['PROCPVs']['FLIR']['numFilter']).get())
            else:
                self.NFilters = 1

            log.info('NDPluginProcess in use, filter type: %s, NFilters: %d s', PV(self.pvlist['PVs']['PROCPVs']['FLIR']['filterCallbacks']).get(as_string=True), self.NFilters)
        else:
            PV(self.pvlist['PVs']['PROCPVs']['FLIR']['ZMQPort']).put('flir', wait=True)
            self.useProcPlugin = False

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
                log.error('BEATS Writer is not running!!!')
                self.epics_pvs['ScanStatus'].put('BEATS Writer is not running!!!')
                repeat = 1
            CLIMessage('BEATS Writer is not running!! Start the writer server to continue the scan AUTOMATICALLY', 'IR')
            time.sleep(0.5)

        repeat = 0
        while PV(self.pvlist['PVs']['writerSuppPVs']['writerFileTrigger']).get() != 0:
            if repeat == 0:
                log.warning('Waiting for BEATS writer | there is a file begin written by the writer')
                self.epics_pvs['ScanStatus'].put('Waiting for BEATS writer')
                repeat = 1
            CLIMessage('BEATS Writer is busey writing a file. The scan will continue AUTOMATICALLY when the writer is ready again', 'IO')
            time.sleep(0.5)

        # Triggers the writer to generate the file and be ready for ZMQ
        PV(self.pvlist['PVs']['writerSuppPVs']['writerFileTrigger']).put(1)

        repeat = 0
        while PV(self.pvlist['PVs']['writerSuppPVs']['writerFileCreated']).get() != 1:
            if repeat == 0:
                log.info('Wating for BEATS Writer to prepare the H5 dxFile.')
                self.epics_pvs['ScanStatus'].put('Creating H5 dxFile')
                repeat = 1
            CLIMessage('BEATS Writer | Wating for H5 dxFile creation', 'IO')
            time.sleep(0.5)

        time.sleep(0.5)
        print ('\n')

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

        if self.useProcPlugin:
            collect_progress = str(int(num_collected / self.NFilters)) + '/' + str(int(num_images / self.NFilters))
        else:
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

        log.info('end scan')
        # Save the configuration
        # Strip the extension from the FullFileName and add .config
        full_file_name = self.SEDPath + '/' + self.SEDFileName
        log.info('data save location: %s', full_file_name)
        config_file_root = os.path.splitext(full_file_name)[0]
        self.save_configuration(config_file_root + '.config')

        # Call the base class method
        super().end_scan()
        # Close shutter
        self.close_shutter()

        ### Only if the proposal ID not valid for users experiments ###
        try:
            if self.breakFlag:
                self.epics_pvs['ScanStatus'].put('Wrong proposal ID or not scheduled, Proposal ID verification')
        except:
            pass

    def save_configuration(self, file_name):
        """Saves the current configuration PVs to a file.

        A new dictionary is created, containing the key for each PV in the ``config_pvs`` dictionary
        and the current value of that PV.  This dictionary is written to the file in JSON format.
        """
        file_name = self.SEDPath + '/' + self.SEDFileName + '.config'

        config = {}
        for key in self.config_pvs:
            config[key] = self.config_pvs[key].get(as_string=True)
        try:
            out_file = f = open(self.SEDBasePath + '/config.config', mode='w', encoding='utf-8')
            json.dump(config, out_file, indent=2)
            out_file.close()
            time.sleep(.1)
            shutil.move (self.SEDBasePath + '/config.config', file_name)

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

    def collect_projections(self):
        """
        This method has been overrided to fit BEATS DAQ System.

        This does the following:
        - Call the superclass collect_projections() function.
        - Set the trigger mode on the camera.
        - Set the camera in acquire mode.
        - Starts the camera acquiring in software trigger mode.
        - Update scan status.
        """

        log.info('collect projections')
        super().collect_projections()

        if self.useProcPlugin:
            self.set_trigger_mode('Software', self.num_angles * self.NFilters)
        else:
            self.set_trigger_mode('Software', self.num_angles)

        # Start the camera
        self.epics_pvs['CamAcquire'].put('Acquire')
        # Need to wait a short time for AcquireBusy to change to 1
        time.sleep(2)
        self.open_shutter()
        self.epics_pvs['HDF5Location'].put(self.epics_pvs['HDF5ProjectionLocation'].value)
        self.epics_pvs['FrameType'].put('Projection')

        start_time = time.time()
        stabilization_time = self.epics_pvs['StabilizationTime'].get()
        log.info('stabilization time %f s', stabilization_time)
        expTime = self.epics_pvs['ExposureTime'].get()

        if self.useProcPlugin:
            avgConter = 0
            if self.epics_pvs['UseExposureShutter'].get():
                for k in range(self.num_angles):
                    if self.scan_is_running:
                        log.info('angle %d: %f', k, self.theta[k])
                        self.epics_pvs['Rotation'].put(self.theta[k], wait=True)
                        time.sleep(stabilization_time)
                        log.info('open exposure shutter')
                        self.epics_pvs['ExposureShutter'].put(1, wait=True)
                        time.sleep(0.1)
                        for img in range(self.NFilters):
                            self.epics_pvs['CamTriggerSoftware'].put(1)
                            avgConter = avgConter+1
                            self.wait_pv(self.epics_pvs['CamNumImagesCounter'], avgConter, 60)
                            self.update_status(start_time)
                        time.sleep(expTime + 0.1)
                        self.epics_pvs['ExposureShutter'].put(0, wait=True)
                        log.info('close exposure shutter')
            else:
                for k in range(self.num_angles):
                    if self.scan_is_running:
                        log.info('angle %d: %f', k, self.theta[k])
                        self.epics_pvs['Rotation'].put(self.theta[k], wait=True)
                        time.sleep(stabilization_time)
                        for img in range(self.NFilters):
                            self.epics_pvs['CamTriggerSoftware'].put(1)
                            avgConter = avgConter+1
                            self.wait_pv(self.epics_pvs['CamNumImagesCounter'], avgConter, 60)
                            self.update_status(start_time)
        else:
            if self.epics_pvs['UseExposureShutter'].get():
                for k in range(self.num_angles):
                    if self.scan_is_running:
                        log.info('angle %d: %f', k, self.theta[k])
                        self.epics_pvs['Rotation'].put(self.theta[k], wait=True)
                        time.sleep(stabilization_time)
                        log.info('open exposure shutter')
                        self.epics_pvs['ExposureShutter'].put(1, wait=True)
                        time.sleep(0.1)
                        self.epics_pvs['CamTriggerSoftware'].put(1)
                        time.sleep(expTime + 0.1)
                        self.epics_pvs['ExposureShutter'].put(0, wait=True)
                        log.info('close exposure shutter')
                        self.wait_pv(self.epics_pvs['CamNumImagesCounter'], k+1, 60)
                        self.update_status(start_time)
            else:
                for k in range(self.num_angles):
                    if self.scan_is_running:
                        log.info('angle %d: %f', k, self.theta[k])
                        self.epics_pvs['Rotation'].put(self.theta[k], wait=True)
                        time.sleep(stabilization_time)
                        self.epics_pvs['CamTriggerSoftware'].put(1)
                        self.wait_pv(self.epics_pvs['CamNumImagesCounter'], k+1, 60)
                        self.update_status(start_time)

        # wait until the last frame is saved (not needed)
        time.sleep(0.5)
        self.update_status(start_time)

    def collect_static_frames(self, num_frames):
        """Collects num_frames images in "Internal" trigger mode for dark fields and flat fields.

        This method has been overrided to fit BEATS DAQ System.

        Parameters
        ----------
        num_frames : int
            Number of frames to collect.
        """

        # This is called when collecting dark fields or flat fields
        log.info('collect static frames: %d', num_frames)

        if self.useProcPlugin:
            self.set_trigger_mode('Internal', num_frames * self.NFilters)
        else:
            self.set_trigger_mode('Internal', num_frames)

        self.epics_pvs['CamAcquire'].put('Acquire')
        # Wait for detector and file plugin to be ready
        time.sleep(0.5)
        frame_time = self.compute_frame_time()

        if self.useProcPlugin:
            collection_time = frame_time * num_frames * self.NFilters
        else:
            collection_time = frame_time * num_frames

        self.wait_camera_done(collection_time + 5.0)

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
                log.warning('Shutter is open in %f s', elapsed_time)
                return
            if not self.scan_is_running:
                exit()
            value = self.epics_pvs['OpenShutterStatusValue'].get()
            time.sleep(1.0)
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.warning('Waiting on shutter to open: %f s', elapsed_time)
            # self.epics_pvs['OpenShutter'].put(value, wait=True)
            if timeout > 0:
                if elapsed_time >= timeout:
                    exit()

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
                log.warning('Shutter is close in %f s', elapsed_time)
                return
            if not self.scan_is_running:
                exit()
            value = self.epics_pvs['CloseShutterStatusValue'].get()
            time.sleep(1.0)
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.warning('Waiting on shutter to close: %f s', elapsed_time)
            # self.epics_pvs['CloseShutter'].put(value, wait=True)
            if timeout > 0:
                if elapsed_time >= timeout:
                   exit()
