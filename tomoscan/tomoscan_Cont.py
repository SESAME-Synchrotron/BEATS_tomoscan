"""Software for tomography scanning with EPICS

   Classes
   -------
   TomoScanCONTINUOUS
     Derived class for tomography scanning with EPICS implementing continuous software based scan
"""

import time
import os
import math
import numpy as np
from tomoscan import TomoScan
from tomoscan import log
from epics import PV
from datetime import timedelta
from SEDSS.SEDSupplements import CLIMessage, CLIInputReq


class TomoScanCont(TomoScan):
    """Derived class used for tomography scanning with EPICS implementing continuous software based scan

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

    def collect_static_frames(self, num_frames):
        """Collects num_frames images in "Internal" trigger mode for dark fields and flat fields.

        Parameters
        ----------
        num_frames : int
            Number of frames to collect.
        """
        # This is called when collecting dark fields or flat fields
        time.sleep(1.5)
        log.info('collect static frames: %d', num_frames)
        self.set_trigger_mode('Internal', num_frames)
        self.epics_pvs['CamAcquire'].put('Acquire')
        # Wait for detector and file plugin to be ready
        time.sleep(0.5)
        frame_time = self.compute_frame_time()
        collection_time = frame_time * num_frames
        self.wait_camera_done(collection_time + 5.0)

    def collect_dark_fields(self):
        """Collects dark field images.
        Calls ``collect_static_frames()`` with the number of images specified
        by the ``NumDarkFields`` PV.
        """

        log.info('collect dark fields')
        super().collect_dark_fields()
        self.collect_static_frames(self.num_dark_fields)

    def collect_flat_fields(self):
        """Collects flat field images.
        Calls ``collect_static_frames()`` with the number of images specified
        by the ``NumFlatFields`` PV.
        """
        log.info('collect flat fields')
        super().collect_flat_fields()
        self.collect_static_frames(self.num_flat_fields)

    def begin_scan(self):
        """Performs the operations needed at the very start of a scan.

        This does the following:

        - Calls the base class method.

        - Set the HDF plugin.
        """
        log.info('begin scan')
        # Call the base class method
        self.epics_pvs['FPFileTemplate'].put("%s%s_%3.3d.h5") # sets FP template 
        super().begin_scan()
        time.sleep(0.1)
        # Write h5 file by writer.
        PV("BEATS:WRITER:NumCapture").put(self.total_images)

        log.info("Calculate continous scan parameters")
        if self.num_angles > 0: 
            self.set_cont_scan_parameters() 

    def end_scan(self):
        """Performs the operations needed at the very end of a scan.

        This does the following:

        - Calls ``save_configuration()``.

        - Put the camera back in "FreeRun" mode and acquiring so the user sees live images.

        - Sets the speed of the rotation stage back to the maximum value.

        - Calls ``move_sample_in()``.

        - Calls the base class method.
        """

        # Put the camera back in FreeRun mode and acquiring
        self.set_trigger_mode('FreeRun', 1)
        # Set the rotation speed to maximum
        self.epics_pvs['RotationSpeed'].put(self.max_rotation_speed)
        # Move the sample in.  Could be out if scan was aborted while taking flat fields
        self.move_sample_in()
        
        super().end_scan()

    def collect_projections(self):
        """Collects projections in fly scan mode.

        This does the following:
        - Sets the scan status message
        - Calls open_shutter()
        - Calls move_sample_in()
        - Sets the HDF5 data location for projection data
        - Sets the FrameType to "Projection"
        - Set the trigger mode on the camera.
        - Set the camera in acquire mode.
        - Starts the camera acquiring in software trigger mode.
        - Update scan status.
        """
       
        # Assign the fly scan angular position to theta[]
        self.theta = self.rotation_start + np.arange(self.num_angles) * self.rotation_step

        log.info('collect projections ...')
        super().collect_projections()

        if self.num_angles > 0:
            log.info('start BEATS Continuous scan')
            self.rotate()
            self.acquire_projections()
        else:
            log.warning('No angles entered ... ')

    def set_cont_scan_parameters(self):
        """
        This method calculates some parameters needed for the continuous scans.
        """
        self.set_exposure_time()
        # Camera response time calculation: 
        counter = 0
        self.set_trigger_mode("Internal", self.num_angles)
        #camera_counter = PV("FLIR:cam1:ArrayCounter_RBV").get()
        camera_counter = self.epics_pvs["CamArrayCounter"].get()
        self.camera_response_time = time.time()
        self.epics_pvs["CamAcquire"].put("Acquire")
        #while PV("FLIR:cam1:ArrayCounter_RBV").get()== camera_counter: 
        while self.epics_pvs["CamArrayCounter"].get() == camera_counter: 
            pass
        timeNow = time.time()
        self.camera_response_time = timeNow - self.camera_response_time
        log.info("Camera response time: {}".format(self.camera_response_time))
        self.epics_pvs["CamAcquire"].put("Done")        
        ###############################################
        # set motor speed: 
        self.set_motor_speed()
        self.go_start_position() 

    def set_motor_speed(self): 
        
        # Compute the time for each frame.
        #frame_time = self.compute_frame_time()
        frame_time = self.exposure_time
        log.info("Frame time: {}".format(frame_time))

        # Set motor speed.
        self.motor_speed = self.rotation_step / frame_time
        #self.motor_speed = self.rotation_step / self.exposure_time
        self.epics_pvs["RotationSpeed"].put(self.motor_speed, wait =True) 
        log.info("Rotation speed: {}".format(self.motor_speed))

        # Compute projections time.
        #self.collect_projections_time =  self.num_angles * frame_time
        #log.info("Collect Projections Time: {}".format(self.collect_projections_time))

        ############# Above is anas's section 
        #self.epics_pvs['RotationSpeed'].put(self.max_rotation_speed)

        # time_per_angle = self.compute_frame_time()
        # CLIMessage("time per angle::::::: {}".format(time_per_angle), "E")
        # speed = self.rotation_step / time_per_angle
        # CLIMessage("speed: :::::: {}".format(speed), "E")

        
        # steps_per_deg = abs(round(1./self.rotation_resolution, 0))
        # CLIMessage("steps_per_deg::::::: {}".format(steps_per_deg), "E")

        # self.motor_speed = math.floor((speed * steps_per_deg)) / steps_per_deg
        # CLIMessage("self.motor_speed::::::: {}".format(self.motor_speed), "E")
        # self.epics_pvs['RotationSpeed'].put(self.motor_speed, wait =True)
        # time.sleep(.5)
        # # Need to read back the actual motor speed because the requested speed might be outside the allowed range
        # self.motor_speed = self.epics_pvs['RotationSpeed'].get()

        # CLIMessage("Accepted motro speed::::::: {}".format(self.motor_speed), "E")
    
    def go_start_position(self): 
        # Put the motor at approparate start position to accelarate and be in a steady speed.

        motorACCLTime = self.control_pvs['RotationAccelTime'].get()
        # Get the distance needed for acceleration = 1/2 a t^2 = 1/2 * v * t.
        accel_dist = motorACCLTime / 2.0 * float(self.motor_speed) 
        
        # Make taxi distance an integer number of measurement.
        # Add 4.5 to ensure that we are really up to speed.
        if self.rotation_step > 0:
            taxi_dist = math.ceil(accel_dist / self.rotation_step + 5) * self.rotation_step 
        else:
            taxi_dist = math.floor(accel_dist / self.rotation_step - 5) * self.rotation_step 

        if self.camera_response_time <= motorACCLTime:
            self.abort_scan()
        else:
            self.start_position = self.rotation_start - taxi_dist 
            self.rotation_stop = (self.rotation_start + (self.num_angles - 1) * self.rotation_step)
            self.end_position = self.rotation_stop + taxi_dist * (self.camera_response_time / self.exposure_time) 
            log.info("Start position: {}, Stop position: {}".format(self.start_position, self.end_position))
            self.epics_pvs['RotationSpeed'].put(self.max_rotation_speed)
            self.epics_pvs["Rotation"].put(self.start_position, wait =True)
            self.epics_pvs['RotationSpeed'].put(self.motor_speed, wait =True)

    def rotate(self):

        log.info("Rotation thread started")
        # log.info("Start position: {}, Stop position: {}".format(self.start_position, self.end_position))
        self.epics_pvs["Rotation"].put(self.end_position)

    def acquire_projections(self):

        log.info("Acquiring projection thread started")
        self.set_trigger_mode("Internal", self.num_angles)
        self.epics_pvs["CamAcquire"].put("Acquire")
        time.sleep(0.5)
        frame_time = self.compute_frame_time()
        collection_time = frame_time * self.num_angles
        self.wait_camera_done(collection_time + 30.0)
    
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
    # def update_status(self, start_time):
    #     """
    #     When called updates ``ImagesCollected``, ``ImagesSaved``, ``ElapsedTime``, and ``RemainingTime``. 

    #     Parameters
    #     ----------
    #     start_time : time

    #         Start time to calculate elapsed time.

    #     Returns
    #     -------
    #     elapsed_time : float

    #         Elapsed time to be used for time out.
    #     """
    #     #num_collected  = self.epics_pvs['CamNumImagesCounter'].value
    #     num_collected   = PV("FLIR:cam1:NumImagesCounter_RBV").get()
    #     num_images     = self.epics_pvs['CamNumImages'].value
    #     num_saved      = PV("BEATS:WRITER:NumSaved").get()
    #     num_saved      += 1 # writer starts from 0  
    #     current_time = time.time()
    #     elapsed_time = current_time - start_time
    #     remaining_time = (elapsed_time * (num_images - num_collected) /
    #                       max(float(num_collected), 1))
    #     collect_progress = str(num_collected) + '/' + str(num_images)
    #     log.info('Collected --------------------------------------- %s', collect_progress)
    #     self.epics_pvs['ImagesCollected'].put(collect_progress)
    #     save_progress = str(num_saved) + '/' + str(self.total_images)
    #     log.info('Saved %s', save_progress)
    #     self.epics_pvs['ImagesSaved'].put(save_progress)
    #     self.epics_pvs['ElapsedTime'].put(str(timedelta(seconds=int(elapsed_time))))
    #     self.epics_pvs['RemainingTime'].put(str(timedelta(seconds=int(remaining_time))))

    #     return elapsed_time

