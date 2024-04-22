=================
Documentation of procedures
=================

The intention of this section is to enable new beamline staff or trainees as quickly as possible to work autonomously at/with the beamline.
Non-routine tasks.

ToDo: Create a documentation for changing cameras and optics/magnifications.

after shutdown
--------------

- do search of the optics hutch

- are all chillers and other devices turned on (e.g. the chiller of the monochromator), are all symbols in the dashboad green? If everything seems ok click reset to refresh them and see if the shutters can be opened.

- open the gauge valves

- check with Yazeed if any motors need to be homed, especially if there was a power cut

- experimental hutch: CVD Window 2: water flow for cooling should be >= 3.5, below 3 it gives an interlock


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

How to switch on the cameras.


changing optics/magnification
---------

Videos + photos


cleaning the scintillator
-----------------------

