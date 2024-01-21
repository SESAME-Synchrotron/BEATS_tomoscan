===============================
BEATS Computing Infrastructure 
===============================

Data analysis workstation
-------------------------
The data analysis workstation is used for several purposes including:

    * Inspection of sinograms and CT reconstruction
    * Submit reconstruction jobs on ``rum@sesame.org.jo``
    * 3D image visualization and processing

The list of software available on the workstation is listed below.

Useful commands:
~~~~~~~~~~~~~~~~
Start `alrecon <https://github.com/gianthk/alrecon/tree/master>`_ CT reconstruction environment::
    conda activate tomopy
    solara run alrecon.pages --host localhost

Start reconstruction pipeline on Jupyter Lab. Available pipelines are described in section :doc:`reconstruction`::
    conda activate tomopy
    jupyter lab

Data analysis software
----------------------
The software in the table below can be used to inspect and process 3D image data (sinograms and CT reconstructions) at SESAME BEATS.

+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+
| Name      | URL                                             | Open source | Features                                                   |
+===========+=================================================+=============+============================================================+
| ImageJ    | https://fiji.sc/                                | yes         | Essential for data collection and reconstruction           |
| Paraview  | https://www.paraview.org/                       | yes         | 3D image rendering                                         |
| Dragonfly | https://www.theobjects.com/dragonfly/index.html | no          | 3D image analysis and visualization                        |
| 3D Slicer | https://www.slicer.org/                         | yes         | 3D image analysis and visualization                        |
| TomoPy    | https://tomopy.readthedocs.io/en/stable/        | yes         | CT reconstruction in Python                                |
| Alrecon   | https://github.com/gianthk/alrecon/tree/master  | yes         | Web app for CT reconstruction                              |
| Jupyter   | https://jupyter.org/                            | yes         | Interface for Python reconstruction pipelines (notebooks)  |
+-----------+-------------------------------------------------+-------------+------------------------------------------------------------+

Load reconstructed volume with ImageJ:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reconstructions at SESAME BEATS are generally saved as a stack of ``.TIFF`` images contained in a reconstruction folder. To load a reconstruction in ImageJ use the command ``File › Import › Image Sequence``.
.. note::
    Select the option ``Use Virtual Stack`` when you import large image sequences!

rum - BEATS reconstruction cluster
----------------------------------

Access the reconstruction cluster ``rum@sesame.org.jo`` with::
    ssh -X beatsbs@rum.sesame.org.jo
