Setup your experiment
=====================

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
    :alt: tomo_user

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

	*Figure 2: BEATS experimental GUI.*