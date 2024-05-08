=================
Documentation of procedures
=================

The intention of this section is to enable new beamline staff or trainees as quickly as possible to work autonomously at/with the beamline.
Non-routine tasks.

ToDo: Create a documentation for changing cameras and optics/magnifications.

Put in filters and observe the beam for the first time. -> adjustment of the beam for the experiment.





alignment too
--------------

Here should be another reference
:ref:`sample alignment<sample alignment>`

:doc:`tomoalign`





after shutdown
--------------

- do search of the optics hutch

- are all chillers and other devices turned on (e.g. the chiller of the monochromator), are all symbols in the dashboad green? If everything seems ok click reset to refresh them and see if the shutters can be opened.

- open the gauge valves

- check with Yazeed if any motors need to be homed, especially if there was a power cut

- experimental hutch: CVD Window 2: water flow for cooling should be >= 3.5, below 3 it gives an interlock





Changing cameras
-------------------------------





Selecting detector, start of IOC, getting initial images
-------------------------------

FLIR needs to be plugged in
PCO needs to be switched on on top, its chiller is in "follow-mode".






Refining slit settings and detector posotion
-------------------------------


Potential obstacles
-------------------------------

could be that wire scanner, diagnostics screen, white beam blocker (WBB), CVD window are "in the beam" and give artefacts


Change radiation and energy settings
-------------------------------

The beamline energy can be changed using the `Energy CLI <https://xray-energy.readthedocs.io/en/latest/usage.html>`_.

.. highlight:: bash
   :linenothreshold: 1

Start the `Energy CLI <https://xray-energy.readthedocs.io/en/latest/usage.html>`_::

   cd /home/control/energy/iocBoot/iocEnergy_2BM
   python3 -i start_energy.py

Set energy to 20.0 keV (W/B4C stripe)::

   energy set --energy 20

Set energy to 20.0 keV (Ru/B4C stripe)::

   energy set --energy 19.99

.. highlight:: none



--- maybe list more settings + filtered radiation?


changing detectors
--------------

Videos + photos

How to switch on the cameras. : plug in power supply or simply switch on


increase distance between sample and detector to e.g. 1m

Det1/Det3 - optique peter:
	remove lead box
	untighten small crews
	place the camera in a safe place (e.g. a hanging, CLEAN bag)
	connections
	
	Det3 (poly radiation): connect all five available cables
	Det3 (mono radiation with objectives): connect Foc1/Rot1
	
	
Det2 - Hasselblad:
	open black housing (heavy, perhaps use the crane)


changing optics/magnification
---------

Videos + photos


cleaning the scintillator
-----------------------



Mount proposal folders
----------------------

.. warning::
    The following commands are for the beamline staff only.

Mount proposal ``ExpData`` and ``recon`` folders on BL-BEATS-WS01::

   cd ~
   ./petra_prop_mounter.sh

Check mount points::

   df -h

Unmount proposal folders::

   umount /PETRA/SED/BEATS/SEM_6/20235010
   umount /PETRA/SED/BEATS/SEM_6_recon/20235010

Mount proposal ``ExpData`` and ``recon`` folders on Win Data Dispenser and Dragonfly VizServer::

   ./petra_prop_recon_smb_mounter.sh

.. highlight:: none

.. note::
    For proposals belonging to a different semester the scripts ``petra_prop_mounter.sh`` and ``petra_prop_recon_smb_mounter.sh`` must be modified.



Endstation alignment
--------------------

.. note::
	The endstation is aligned by the beamline staff at the start of your beamtime. Generally, you don't need to repeat these operation and you can jump to :ref:`sample alignment<sample alignment>`

1. Endstation pitch
2. Endstation X-axis
3. Camera rotation
4. Detector focus

.. _sample alignment:

