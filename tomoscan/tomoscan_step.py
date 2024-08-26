"""Software for tomography scanning with EPICS

   Classes
   -------
   TomoScanSTEP
     Derived class for tomography scanning with EPICS implementing step scan
"""

import time
import numpy as np
from tomoscan.tomoscan import TomoScan
from tomoscan import log

from epics import PV

class TomoScanSTEP(TomoScan):
    """Derived class used for tomography scanning with EPICS implementing step scan

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

        self.epics_pvs['ExposureShutter'].put(1, wait=True)
        time.sleep(0.01)
        log.info('collect flat fields')
        super().collect_flat_fields()
        self.collect_static_frames(self.num_flat_fields)
        self.epics_pvs['ExposureShutter'].put(0, wait=True)

    def begin_scan(self):
        """Performs the operations needed at the very start of a scan.

        This does the following:

        - Calls the base class method.

        - Set the HDF plugin.
        """

        log.info('begin scan')
        # Call the base class method
        super().begin_scan()

        self.collect_frames_to_init_det()

        # Set angles for the interlaced scan
        self.theta = self.rotation_start + np.arange(self.num_angles) * self.rotation_step

    def collect_frames_to_init_det(self):
        """
        This method collects some frames ahead of each scan in order
        to make the camera ready (i.e. let the camera calculate frame dimensions
        which might be 0 after restarting the camera IOC).
        this is mainly needed for the writer to run in perfect conditions
        """

        self.set_exposure_time()
        self.set_trigger_mode('Internal', self.num_angles)
        camera_counter = self.epics_pvs['CamArrayCounter'].get()
        self.epics_pvs['CamAcquire'].put('Acquire')
        while self.epics_pvs['CamArrayCounter'].get() == camera_counter:
            pass
        self.epics_pvs['CamAcquire'].put('Done')

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
