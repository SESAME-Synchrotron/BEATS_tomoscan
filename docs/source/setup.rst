Beamline setup
==============

To start the main BEATS control GUI type:

::

	$ beats-qt

.. figure:: /img/beats-qt_annotated.png
	:align: center
	:alt: BEATS beamline GUI

	*Figure 1: BEATS beamline control GUI.*

In addition, the ``beats-qt`` GUI allows to:

#. Display of the machine status and parameters.
#. Launch the BEATS :ref:`Beamline vacuum GUI`. The vacuum GUI is used to open the shutters of the beamline.
#. Launch the BEATS :ref:`Experimental GUI`. This GUI controls the sample manipulator and detection systems.


.. class:: remove
	.. note::
		The beamline is setup for your experiment at the start of the beamtime together with the beamline staff. Most of the times, there will be nothing to change from one scan to the next. Ask the beamline staff before changing any beamline setting.

	The beamline control GUI allows to control the in-vacuum instrumentation in the beamline front-end, optics hutch, and experimental hutch. In particular, you might need to adjust the configuration of:

	* One or more of the beamline slits
	* Attenuator system
	* Double Multilayer Monochromator
