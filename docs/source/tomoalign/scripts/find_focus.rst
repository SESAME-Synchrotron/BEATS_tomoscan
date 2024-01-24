Script ``find_focus.py``
========================

Script to perform an automatic focus search at the TOMCAT beamline.

For more information, display the script's help text

.. code-block:: shell

    find_focus.py -h

Examples:
---------

* Perform a completely automatic focus search::

    find_focus.py

* Perform a focus search with a set of specified step sizes::

    find_focus.py -s "100,10,1"

* Perform a search starting at a position of 1800, using a specific set of step sizes and overshoot values, and setting a limit of 3200 for the highest search position::

    find_focus.py -s "100,10,1" -o "3,8,25" -s 1800 -m 3200

  This will run three iterations of the search process. The first one with a step size of 100 and an overshoot of 3 steps, the second one with a step size of 10 and an overshoot of 8 steps, and the third one with a step size of 1 and an overshoot of 25 steps.
