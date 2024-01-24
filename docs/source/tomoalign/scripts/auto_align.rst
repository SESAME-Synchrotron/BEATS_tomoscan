Script ``auto_align.py``
========================

Script to perform an automatic camera alignment (tilt & center).

For more information, display the script's help text

.. code-block:: shell

    auto_align.py -h

Examples:
---------

* Perform a completely automatic alignment::

    auto_align.py

* Perform the alignment to a specified minimum accuracy (0.8 pixels for the rotation and 1.0 pixels for the centering)::

    auto_align.py -r 0.8 -c 1.0

* Limit the maximum number of iterations to 8::

    auto_align.py -i 8

