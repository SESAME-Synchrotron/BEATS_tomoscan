BEATS Dashboard
================

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

Selecting Process
------------------

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

.. warning:: Make sure the TCPServerSocket.py is running on the server.
	
.. warning:: There is an interlocking between (Start, Stop, Restart) for all operations, depending on the status of the IOCs, whether they are running or not.
	
.. warning:: If one of the common IOCs is stopped, the other controlling sections will be disabled until all the common IOCs are running.
	
.. warning:: If the combined stopper shutter has a fault or the PSS is interlocked, the DAQ Tomoscan will be available only in *Testing Mode*.
	
.. note:: In the scanning techniques section, the python server (start button) is disabled until the tomoscan IOC is started.
	
.. warning:: There is an interlocking between the scanning techniques. This means that if any other scanning is started while the first one is still running, the first scanning will be automatically halted.
	
.. warning:: If the detector's IOC is stopped and you select any detector type, you cannot start the scan until the IOC is running.
	
.. note:: If the GUI is unexpectedly closed and then reopened, selecting one of the detectors will show the current choice if one of the other sections is hidden or disabled.
	