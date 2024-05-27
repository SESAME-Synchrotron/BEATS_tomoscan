
Quick start guide
=================

Welcome to ID-10 BEATS. Below is a coarse overview of the most important steps to setup and perform your first scan. To keep to page simple but provide all information needed, links to in depth descriptions are provided in the corresponding sections.

.. note::
    The beamline is setup for your experiment at the start of the beamtime together with the beamline staff. This includes energy adjustment and mounting detector and optics. Most of the times, there will be little to change from one scan to the next, besides aligning the sample. Ask the beamline staff before changing any beamline setting.





Getting started
--------------------

The beamline control GUI allows to control the in-vacuum instrumentation in the beamline front-end, optics hutch, and experimental hutch.

Here are things users should be comfortable doing during their experiments.

In particular, you might need to adjust the configuration of:

* One or more of the beamline slits
* Attenuator system
* search the hutch and open the shutters
* adjust the sample on the stage
* start a scan

The heartpiece of beamline operation is the ``beats-qt`` GUI.


.. figure:: /img/beats-qt_annotated.png
	:align: center
	:alt: BEATS beamline GUI

	*Figure 1: BEATS beamline control GUI.*


If it's not already started or gets closed accidentally, it can be started from a linux console on the control computer (e.g. by pressing ctrl + alt + t) and typing

::

	$ beats-qt

The BEATS beamline GUI allows to
#. display the machine status and parameters.
#. launch the BEATS :ref:`Beamline vacuum GUI`. The vacuum GUI is used to open the shutters of the beamline.
#. launch the BEATS :ref:`Experimental GUI`. This GUI controls the sample manipulator and detection systems.





Beamline vacuum GUI
--------------------

To be able to acquire meaningful data, you need to have X-rays on your sample. Therefore, the shutters need to be opened at least. Open the shutters only when needed and you want to measure (also to protect your sample). Openening the shutters can only be performed after the hutch has been searched.

.. figure:: /img/vacuum.png
	:align: center
	:alt: BEATS vacuum GUI

	*Figure 1: BEATS vacuum GUI.*

To open the beamline light path, the shutters must be opened in the following order:
    1. Radiation shutter.
    2. Photon shutter.
    3. Combined stopper.

.. note::
    It is only allowed to open the beamline shutters once the hutches have been searched. You will see a red button besides one of the shutter if opening is not allowed.

.. warning::
    Before opening the beamline shutters for the first time, verify with your local contact the setup of the beamline (slits, attenuator, ...).





Search the hutch
--------------------

.. toctree::
   :maxdepth: 2

   Search the hutch <safety/hutch_search>




  
Start streaming data
--------------------


To access the BEATS Dashboard, type the following command:
::

	$ BEATS_DAQ_Control_Monitor


the main GUI will appear:

.. figure:: /img/dashboard.png
	:align: center
	:alt: BEATS_Dashboard GUI

	*Figure 1: BEATS Dashboard main window*

For a very detailed description of the procedure go to :doc:`dashboard_mainWindow`!





Set up your experiment
--------------------

.. note::
	The endstation is aligned by the beamline staff at the start of your beamtime. Generally, you don't need to repeat these operation and you can jump to :ref:`sample alignment<sample alignment>`


.. toctree::
   :maxdepth: 2

   Set up your experiment <sample_mount>
   
   
   
   
	.. warning::
		**Collision danger**: Only perform this operation together with the beamline staff. You must always pay attention to the position of endstation, detectors and sample, while performing the alignment. **Always move small steps when endstation and detector are close to each other!** 

	.. figure:: /img/beats_endstation1.jpg
		:align: center
		:alt: BEATS experimental station

		*Figure 1: BEATS experimental station. Two laser lines are used to pre-align sample and detector on the beam.*

	Preliminary steps
	-----------------

	#. Mount your sample on top of the tomography endstation (Figure 1 RIGHT)
	#. Turn on the alignment lasers
	#. Use the laptop close to the endstation to:

	   #. Pre-align sample on the intersection of the laser planes (you can verify this also moving the ROT stage)
	   #. Pre-align the detector scintillator on the same line
	   #. Set the distance between sample and detector to the desired value

	Sample mount
	------------

	* Samples can be mounted on the tomography rotation stage with M4 screws as shown Figure 2.

	* A set of standard kinematic mounts from Newport is also available: `M-BK-1A <https://www.newport.com/p/M-BK-1A>`_ (download -> `drawing <https://www.newport.com/medias/sys_master/images/images/h7a/h3c/8933922308126/BK-1-S.pdf>`_).

	.. figure:: /img/beats_sample_mount.png
		:align: center
		:alt: Sample mounting at BEATS

		*Figure 2: (LEFT) Detail of sample tomography stage. (RIGHT) The sample plate has 9 M4 holes that can be used for custom sample support.*

	Sample alignment
	----------------

	| In order to align the sample on the center of rotation of the rotary stage 4 motorized axis are needed:
	|
	| • **TOMO_Y** (vertical motion)
	| • **TOMO_X** (horizontal motion perpendicular to the beam)
	| • **SAMPLE_SX** (horizontal motion above the rotary stage)
	| • **SAMPLE_SZ** (horizontal motion normal to "sample top X" above the rotary stage)

	| The motion range of the tomography endstation (Figure 1 RIGHT) is:
	|
	| • **TOMO_X**: 60.0 mm
	| • **TOMO_Y**: 47.0 mm

	Sample alignment procedure
	~~~~~~~~~~~~~~~~~~~~~~~~~~

	Load the sample on the kinematic mount (for automatic alignemt of the endstation with :doc:`tomoalign` use the tungsten wire available at the beamline as sample) then:

	#. Perform the :doc:`hutch_search`
	#. Open the shutters using the :doc:`vacuum`
	#. Use the :ref:`Experimental GUI` to move the sample up/down until the sample is in the field of view of detector.

	Experimental GUI
	----------------

	.. figure:: /img/exp_gui.png
		:align: center
		:alt: BEATS experimental GUI

		*Figure 3: BEATS experimental GUI.*
  
  
   



   
Reconstruct your data
--------------------

.. toctree::
   :maxdepth: 2

   7. Reconstruct your data <quick_reconstruction>


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~