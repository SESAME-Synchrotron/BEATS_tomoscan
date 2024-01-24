Script ``auto_focus.py``
========================

Script to automatically focus the microscope/camera setup at TOMCAT.

For more information, display the script's help text

.. code-block:: shell

    auto_focus.py -h

Examples:
---------

* Run a completely automatic autofocussing procedure::

    auto_focus.py

* Run an autofocussing procedure with a specified step size of 0.5 microns over a range of +/- 35 microns around the start position at 2430 um::

    auto_focus.py -s 0.5 -r 35 -p 2430
