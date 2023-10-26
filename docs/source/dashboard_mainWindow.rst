.. _dashboard:


BEATS Dashboard
================

This dashboard has been developed to help in the starting tomoscan scanning process by allowing the user to monitor and control everything associated with tomoscan.

To access the BEATS Dashboard, type the following command:
::

	$ BEATS_DAQ_Control_Monitor


the main GUI will appear:

.. figure:: /img/dashboard.png
	:align: center
	:alt: BEATS_Dashboard GUI

	*Figure 1: BEATS Dashboard main window*

The BEATS Dashboard shown below is divided into three sections for controlling and five sections for monitoring:

.. figure:: /img/dashboard_sections.png
	:align: center
	:alt: BEATS_DashboardSections

	*Figure 2: BEATS Dashboard sections*


Controlling Sections:
	* 1) Common IOCs: These are the mandatory EPICS BEATS IOCs for scanning.
		-Shutter IOC.
		-Motor IOC.
		-TomoScan Support IOC.
		-Writer Support IOC.
		-SSCAN IOC.

	* 2) Detector Type: The available detectors for the scanning.
		-Detector Status (indicate if the (hardware, Software) is connected or not (Power, Ethernet, IOC)).
		-Detector IOC.
		-Detector Driver.

	* 3) Scanning Methodology: The available scanning techniques for BEATS beamline.
		-Step Scan:
			* TomoScan IOC.
			* Python Server.
			* writer Server.
			* MEDM (TomoScan MEDM)

		-Continuous Scan:
			* TomoScan IOC.
			* Python Server.
			* writer Server.
			* MEDM (TomoScan MEDM)


Monitoring Sections:
	* A) The detector type and the scanning technique are chosen.
	* B) The online logging (last log).
	* C) Shutters Status.
	* D) Current tomoscan mode.
	* E) The current detector chosen & current rotation stage.

Other Features
................

The following new features have been added to the BEATS dashboard:

1. ImageJ: starts imageJ viewer.
2. :ref:`singleShotImage`.
3. Rot. Internal Movement Speed: the speed of the micos rotary stage that tomoscan set when go to max speed.

Selecting Process
..................

The user has the option to choose the detector after opening the main window. Once the user has selected a detector, the *Current Chosen Detector* will display their selection.
Following that, the user has the option to choose the scanning technique. Once the user has selected a scanning method (started the Tomoscan IOC), the *detector type and scanning technique* will display their choice. Additionally, as shown below, the other types of detectors will be disabled and the other scanning techniques hidden.

.. figure:: /img/dashboard_selectingProcess.png
	:align: center
	:alt: BEATS_SelectingProcess

	*Figure 3: Selecting Process of Scanning Technique*

To change the detector type or scanning technique, the current process (TomoScan) must be stopped.

.. note::

	All operations will be opened in tmux sessions, to attach any session, write the following commands:

	::

		$ tmux ls
		$ tmux a -t "session name"
		$ Esc, Ctrl b, d (to detach the session)


------------------------------------------------------------------------------------

.. warning::

	Make sure the TCPServerSocket.py is running on the server.

.. warning::

	There is an interlocking between (Start, Stop, Restart) for all operations, depending on the status of the IOCs, whether they are running or not.

.. warning::

	If one of the common IOCs is stopped (except SSCAN IOC), the other controlling sections will be disabled until all the common IOCs are running.

.. warning::

	If the combined stopper shutter has a fault or the PSS is interlocked, the DAQ Tomoscan will be available only in *Testing Mode*.

.. note::

	In the scanning techniques section, the python server (start button) is disabled until the tomoscan IOC is started.

.. warning::

	There is an interlocking between the scanning techniques. This means that if any other scanning is started while the first one is still running, the first scanning will be automatically halted.

.. warning::

	If the detector's IOC is stopped and you select any detector type, you cannot start the scan until the IOC is running.

.. note::

	If the GUI is unexpectedly closed and then reopened, selecting one of the detectors will show the current choice if one of the other sections is hidden or disabled.


.. _singleShotImage:

Single Shot Image
------------------

The fundamental idea behind a single shot image is to capture one or more frames based on the capturing type chosen.
To begin this process, once opened, its features will be disabled as shown in the figure.4, and you must type the detector's prefix (TEST-PCO: or FLIR:) to be able to proceed as shown in the figure.5.

.. note::

	The Single Shot Image main window button will be disabled if any tomoscan mode is running.


.. figure:: /img/singleShotImage.png
	:align: center
	:scale: 75 %
	:alt: SingleShotImageMainWindow

	*Figure 4: Single Shot Image -Main Window-*


.. figure:: /img/singleShotImagePrefix.png
	:align: center
	:scale: 75 %
	:alt: SingleShotImagePrefix

	*Figure 4: Single Shot Image -Available Prefixes-*

The redout and collect sections, which contain the detector's parameters, become active once you type the prefix.

The available capture modes are as follows:

1. Single Image Acquiring
..........................

The idea behind this mode is to open the exposure shutter, take one shot, and then close the exposure shutter.

Both clicking the "Acquire" button or using the "Space" key will initiate the acquisition process. The image can also be saved (TIFF or PNG format).

	.. figure:: /img/singleShotImageStart.png
		:align: center
		:scale: 75 %
		:alt: SingleShotImageStart

		*Figure 5: Single Shot Image -Main Parameters-*

.. note::

	To save the image, you have to determine the path and define the image name only *without any extension*. Moreover you will be alerted if the path is not valid.

.. note::

	The acquiring process is shown in the main terminal as figure below. Moreover, the *Status yellow field* shows the last log.

	.. figure:: /img/singleShotImageTerminal.png
		:align: center
		:alt: SingleShotImageTerminal

		*Figure 6: Single Shot Image -Acquiring Process-*

2. SSCAN
..........

The idea behind this mode is to collect multiple images for each motion step. more info can be found here: `SSCAN reference <https://epics-modules.github.io/sscan/>`_

The main *write fields* parameters of SSCAN section are:
	- File name
	- File format (the main format is h5 file)
	- Next file number

The figure below will appear after clicking on the desired SSCAN dimension; you can start SSCAN up to 4 dimensions.
	.. figure:: /img/SSCANMainWindow.png
		:align: center
		:scale: 75 %
		:alt: SSCAN

		*Figure 6: Single Shot Image -Acquiring Process-*

.. note::

	The trigger PVs to start acquiring for both detectors are:
	- for PCO: TEST-PCO:cam1:Acquire
	- for FLIR: FLIR:cam1:TriggerSoftware

.. note::

	Very Important!
	You must ensure that the data from the detector are gathered; the value for the *Capturing?* field should be (Capture yellow Colored instead of Done).

.. note::

	The file extension of SSCAN outout is binary format (.mda), to read it you have to convert it to txt file.
	::
		******Script*****

 ***** saving data

check dev docs
