
Quick start guide
=================

Welcome to ID-10 BEATS. Follow the steps below to setup and perform your first scan.

.. note::
    The beamline is setup for your experiment at the start of the beamtime together with the beamline staff. Most of the times, there will be nothing to change from one scan to the next. Ask the beamline staff before changing any beamline setting.

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

It can be started from a linux console on the control computer (e.g. by pressing ctrl + alt + t) and typing

::

	$ beats-qt

The BEATS beamline GUI allows to
#. display the machine status and parameters.
#. launch the BEATS :ref:`Beamline vacuum GUI`. The vacuum GUI is used to open the shutters of the beamline.
#. launch the BEATS :ref:`Experimental GUI`. This GUI controls the sample manipulator and detection systems.



.. toctree::
   :maxdepth: 2

   1. Set up the beamline <setup>
   2. Set up your experiment <sample_mount>
   3. Search the hutch <safety/hutch_search>
   4. Open the shutters <vacuum>
   5. Set up the scan <experimental>
   6. Collect data <collect_data>
   7. Reconstruct your data <quick_reconstruction>
   