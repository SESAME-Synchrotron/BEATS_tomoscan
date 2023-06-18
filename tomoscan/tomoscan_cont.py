"""Software for tomography scanning with EPICS

   Classes
   -------
   TomoScanCont
     Derived class for tomography scanning with EPICS implementing continuous software based scan
"""

import time
import os
import math
import numpy as np
from tomoscan import TomoScan
from tomoscan import log
from epics import PV
from SEDSS.CLIMessage import CLIMessage


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
        super().begin_scan()
        time.sleep(0.1)

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
        self.epics_pvs['ExposureShutter'].put(0, wait=True)
        log.info('Close exposure shutter')
        self.move_sample_in()
        self.epics_pvs['ExposureShutter'].put(1, wait=True)
        log.info('Open exposure shutter')
        # Call the base class method
        super().end_scan()

    def collect_projections(self):
        """
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
       
        # Assign the continuous scan angular position to theta[]
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
        self.set_trigger_mode("FreeRun", 1)
        camera_counter = self.epics_pvs["CamArrayCounter"].get()
        self.camera_response_time = time.time()
        self.epics_pvs["CamAcquire"].put("Acquire")
        while self.epics_pvs["CamArrayCounter"].get() == camera_counter: 
            pass
        timeNow = time.time()
        self.camera_response_time = timeNow - self.camera_response_time
        log.info("Camera response time: {}".format(self.camera_response_time))
        
        try: 
            self.camera_fps = self.control_pvs['ResultingFPS'].get(timeout=1)
        except:
            log.error("Unable to get Camera FPS")
            self.abort_scan()
        
        log.info("Camera FPS: {}".format(self.camera_fps))

        self.epics_pvs["CamAcquire"].put("Done")
        self.set_trigger_mode("Internal", self.num_angles)

        self.set_motor_speed()
        self.go_start_position() 

    def set_motor_speed(self):
        # Compute the time for each frame.
        ### =========== frame_time = self.exposure_time
        frame_time = 1/self.camera_fps
        log.info("Frame time: {}".format(frame_time))

        # Set motor speed.
        self.motor_speed = self.rotation_step / frame_time
        self.epics_pvs["RotationSpeed"].put(self.motor_speed, wait =True) 
        self.epics_pvs['CalculatedRotSpeed'].put(self.motor_speed, wait =True)
        log.info("Rotation speed: {}".format(self.motor_speed))
    
    def go_start_position(self): 
        # Put the motor at appropriate start position to accelarate and be in a steady speed.

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
            log.error("Camera response time is less than motorACCLTime")
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
        self.epics_pvs["Rotation"].put(self.end_position)

    def acquire_projections(self):

        log.info("Acquiring projection thread started")
        self.set_trigger_mode("Internal", self.num_angles)
        self.epics_pvs["CamAcquire"].put("Acquire")
        time.sleep(0.5)
        frame_time = self.compute_frame_time()
        collection_time = frame_time * self.num_angles
        self.wait_camera_done(collection_time + 30.0)