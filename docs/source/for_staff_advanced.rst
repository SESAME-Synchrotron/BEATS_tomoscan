=================
Documentation of procedures
=================

The intention of this section is to enable new beamline staff or trainees as quickly as possible to work autonomously at/with the beamline.
Non-routine tasks.

before starting the first time!!!!!
-----------------------------------

Put in filters and observe the beam for the first time. -> adjustment of the beam for the experiment.





after shutdown
--------------

- do search of the optics hutch

- are all chillers and other devices turned on (e.g. the chiller of the monochromator), are all symbols in the dashboad green? If everything seems ok click reset to refresh them and see if the shutters can be opened.

- open the gauge valves

- check with Yazeed if any motors need to be homed, especially if there was a power cut

- experimental hutch: CVD Window 2: water flow for cooling should be >= 3.5, below 3 it gives an interlock





Changing cameras
-------------------------------

open small screws, disconnect and store or mount in a save place the detached camera





Selecting detector, start of IOC, getting initial images
-------------------------------

FLIR needs to be plugged in the power outlet
PCO needs to be switched on on top, its chiller is in "follow-mode".





Refining slit settings and detector position
-------------------------------
slits 1, 2, 3 need to be adapted to fit the FOV





Potential obstacles
-------------------------------

could be that wire scanner, diagnostics screen, white beam blocker (WBB), CVD window are "in the beam" and give artefacts

writer server, tomoscan IOC, and python server need to be restarted from time to time (if they start becoming non-responsive); sometimes it also happens after aborting a scan

At very high energies, owing to total external reflection in the monochromator's layers, filtering of the incoming white beam might be necessary to obtain meaningful data




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



--- maybe list more settings + filtered radiation? ---- orange suite





changing detectors
--------------

Videos + photos

-> increase distance between sample and detector to e.g. 1m
-> remove the camera
-> open screws on the sides
-> slide detector down (get help if it is too heavy for you alone)


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

Videos + photos





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

.. toctree::
   :maxdepth: 2

   Tomoalign - pitch, focus, camera rotation <tomoalign>

   Additional (can be deleted after final checks) :ref:`sample alignment<sample alignment>`