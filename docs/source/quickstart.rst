
Quick start guide
=================

Welcome to ID-10 BEATS. Follow the steps below to setup and perform your first scan.

.. note::
    The beamline is setup for your experiment at the start of the beamtime together with the beamline staff. This includes energy adjustment and mounting detector and optics. Most of the times, there will be little to change from one scan to the next, besides aligning the sample. Ask the beamline staff before changing any beamline setting.

Main points of this page include:

.. toctree::
   :maxdepth: 2

   1. Set up the beamline - link to setup removed
   2. Set up your experiment sample_mount <hallo>
   3. Search the hutch <safety/hutch_search> - still there
   4. Open the shutters - link to vacuum removed
   5. Set up the scan <experimental> - test
   6. Collect data <collect_data>
   7. Reconstruct your data - moved quick_reconstruction

Getting started
--------------------


The beamline control GUI allows to control the in-vacuum instrumentation in the beamline front-end, optics hutch, and experimental hutch.

Here are things users should be comfortable doing during their experiments.

In particular, you might need to adjust the configuration of:

* One or more of the beamline slits
* Attenuator system
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

.. toctree::
   :maxdepth: 2

   Set up your experiment <sample_mount>
   
   
Reconstruct your data
--------------------

.. toctree::
   :maxdepth: 2

   7. Reconstruct your data <quick_reconstruction>


test

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~