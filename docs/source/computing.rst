===============================
BEATS Computing Infrastructure 
===============================

DAQ workstation - ``BEATS-control-ws``
--------------------------------------

The data acquisition (DAQ) workstation is used to control the beamline and scan settings. Visit the section :doc:`daq` for more information.

Useful commands
~~~~~~~~~~~~~~~

.. highlight:: bash
   :linenothreshold: 1

Mount ``PETRA``::

   sudo mount -t nfs 10.1.14.100:/PETRA/SED/BEATS/IH /PETRA/SED/BEATS/IH

SMB mount of SSCAN data folder::

   sudo mount -t cifs -o vers=3,username=beats.smb '\\10.1.14.100\pco-flir-ws' /home/control/Desktop/SSCAN

Start the `Energy GUI <https://xray-energy.readthedocs.io/en/latest/>`_::

   cd /home/control/energy/iocBoot/iocEnergy_2BM
   python3 -i start_energy.py

.. highlight:: none


Data analysis workstation - ``BL-BEATS-WS01``
---------------------------------------------
The data analysis workstation is used for several purposes including:

    * Inspection of sinograms and CT reconstruction
    * Submit reconstruction jobs on the cluster ``rum@sesame.org.jo``
    * 3D image visualization and processing

The list of software available on the workstation is listed in the section on :ref:'Data analysis software' below.

Useful commands
~~~~~~~~~~~~~~~

.. highlight:: bash
   :linenothreshold: 1

Start `alrecon <https://github.com/gianthk/alrecon/tree/master>`_ CT reconstruction environment::

    conda activate tomopy
    solara run alrecon.pages --host localhost

Start reconstruction pipeline on Jupyter Lab. Available pipelines are described in section :doc:`reconstruction`::

    conda activate tomopy
    jupyter lab

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

Data analysis software
----------------------
The software in the table below can be used to inspect and process 3D image data (sinograms and CT reconstructions) at SESAME BEATS.

+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| Name      | URL                                             | Open source | Features                                                   |
+===========+=================================================+=============+============================================================+
| ImageJ    | https://fiji.sc/                                | yes         | Essential for data collection and reconstruction           |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| Paraview  | https://www.paraview.org/                       | yes         | 3D image rendering                                         |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| Dragonfly | https://www.theobjects.com/dragonfly/index.html | no          | 3D image analysis and visualization                        |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| 3D Slicer | https://www.slicer.org/                         | yes         | 3D image analysis and visualization                        |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| TomoPy    | https://tomopy.readthedocs.io/en/stable/        | yes         | CT reconstruction in Python                                |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| Alrecon   | https://github.com/gianthk/alrecon/tree/master  | yes         | Web app for CT reconstruction                              |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| Jupyter   | https://jupyter.org/                            | yes         | Interface for Python reconstruction pipelines (notebooks)  |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+

Load reconstructed volume with ImageJ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reconstructions at SESAME BEATS are generally saved as a stack of ``.TIFF`` images contained in a reconstruction folder. To load a reconstruction in ImageJ use the command ``File › Import › Image Sequence``. You can follow `this video <https://www.youtube.com/watch?v=rmQwHGap2ko>`_ for a detailed explanation on how to import image sequences.

.. figure:: /img/imagej_image_sequence.png
   :align: center
   :alt: Import image sequence in ImageJ

.. note::
   Always select the option ``Use Virtual Stack`` when you import large image stacks in ImageJ!

rum - BEATS reconstruction cluster
----------------------------------

.. highlight:: bash

Access the reconstruction cluster ``rum@sesame.org.jo`` with::

    ssh -X beatsbs@rum.sesame.org.jo

.. highlight:: none

Data dispenser PC
-----------------

Dragonfly VizServer
-------------------

SESAME data portal
------------------

