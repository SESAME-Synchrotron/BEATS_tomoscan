=================
Scripts reference
=================

This section contains the reference and usage information for the scripts
provided by the TomoAlign package.

Script ``auto_focus.py``
------------------------

Script to automatically focus the microscope/camera setup at TOMCAT.

For more information, display the script's help text

.. code-block:: shell

    auto_focus.py -h

Examples:
~~~~~~~~~

* Run a completely automatic autofocussing procedure::

    auto_focus.py

* Run an autofocussing procedure with a specified step size of 0.5 microns over a range of +/- 35 microns around the start position at 2430 um::

    auto_focus.py -s 0.5 -r 35 -p 2430


Script ``find_focus.py``
------------------------

Script to perform an automatic focus search at the TOMCAT beamline.

For more information, display the script's help text

.. code-block:: shell

    find_focus.py -h

Examples:
~~~~~~~~~

* Perform a completely automatic focus search::

    find_focus.py

* Perform a focus search with a set of specified step sizes::

    find_focus.py -s "100,10,1"

* Perform a search starting at a position of 1800, using a specific set of step sizes and overshoot values, and setting a limit of 3200 for the highest search position::

    find_focus.py -s "100,10,1" -o "3,8,25" -s 1800 -m 3200

This will run three iterations of the search process. The first one with a step size of 100 and an overshoot of 3 steps, the second one with a step size of 10 and an overshoot of 8 steps, and the third one with a step size of 1 and an overshoot of 25 steps.

Script ``auto_align.py``
------------------------

Script to perform an automatic camera alignment (tilt & center).

For more information, display the script's help text

.. code-block:: shell

    auto_align.py -h

Examples:
~~~~~~~~~

* Perform a completely automatic alignment::

    auto_align.py

* Perform the alignment to a specified minimum accuracy (0.8 pixels for the rotation and 1.0 pixels for the centering)::

    auto_align.py -r 0.8 -c 1.0

* Limit the maximum number of iterations to 8::

    auto_align.py -i 8

