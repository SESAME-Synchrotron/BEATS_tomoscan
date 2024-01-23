Installation
============

Installation at TOMCAT
----------------------

The tomoalign package should already be installed at the TOMCAT beamline for
general use. The installation location is::

    /sls/X02DA/applications/tomoalign

This directory simply contains a clone of the git repository. Additionally, all
of the common scripts for alignment procedures are directly linked to from the
beamline's binary directory ``/sls/X02DA/bin`` so they can be called directly
from the command line on any beamline console.

If you intend to import the tomoalign package from a custom script, you may
have to either add the beamline installation location to the ``PYTHONPATH`` or
clone the repository locally and then add it to the python search path. For the
former approach, something like this might do the trick:

.. code-block:: python
   :linenos:

   import sys
   sys.path.insert(0, '/sls/X02DA/applications/tomoalign')
   import tomoalign

Local installation
------------------
To install the tomoalign package locally, simply clone the repository in a
convenient location and import the package directly from there. See above for
how to add the new local path to the ``PYTHONPATH``.

A conda-packaged version of the repository is planned to be released soon.

Prerequisites
-------------

tomoalign was written and developed on python 2.7 and 3.6, and should thus work
on most flavors of python.

Dependencies
------------
The tomoalign package depends on the following packages:

* h5py
* lmfit
* matplotlib
* numpy
* pyepics
* scipy
* skimage
