#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to perform an automatic focus search at the TOMCAT beamline.

For more information, display the script's help text

.. code-block:: shell

    find_focus.py -h

"""

# Note regarding the script layout
# --------------------------------
# Separating the argument parser from the main script's code enables the
# automatic generation of script documentation with the sphinx-argparse
# extension.
# The actual script code should only be executed if the script is called
# directly (i.e.: if __name__ = "__main__"). This allows the script module
# to be imported by another program (e.g.: the sphinx-builder) without
# actually running the script code itself.


import argparse
import numpy as np
import textwrap


def get_argument_parser():
    """
    Helper function to create and return the parser object for the command
    line arguments.
    """

    description = textwrap.dedent('''\
        Script to perform an automatic focus search.

        The search starts from a specified start position in the positive focus
        direction. Typically, the search is iterated a few times, starting with
        coarse search steps, and narrowing in on the true focus position with
        increasingly finer steps.

        The algorithm is trying to detect a peak in the focus metrics. Once a
        peak has been identfied in one iteration, a narrower region around the
        peak position is scanned with finer and finer steps until the smallest
        step size is reached.
        ''')
    epilog = textwrap.dedent('''\
        EXAMPLES:

        * Perform a completely automatic focus search::

            find_focus.py

        * Perform a focus search with a set of specified step sizes::

            find_focus.py -s "100,10,1"

        * Perform a search starting at a position of 1800, using a specific set
          of step sizes and overshoot values, and setting a limit of 3200 for
          the highest search position::

            find_focus.py -s "100,10,1" -o "3,8,25" -s 1800 -m 3200

          This will run three iterations of the search process. The first one
          with a step size of 100 and an overshoot of 3 steps, the second one
          with a step size of 10 and an overshoot of 8 steps, and the third
          one with a step size of 1 and an overshoot of 25 steps.

        ''')
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--stepsizes", type=str, default="",
        help=('The step sizes to use for each iteration of the search, '
            'ordered from largest to smallest. The length of the array '
            'determines the number of iterations that will be performed. If '
            'empty (""), the function tries to determine a sensible set of '
            'step sizes automatically. Lists of steps must be separated by '
            'commas and enclosed in quotes, e.g.: "100,10,1". '
            '(default = %(default)s)'))
    parser.add_argument("-o", "--overshoot", type=str, default="",
        help=('The minimum number of steps to be recorded after the peak '
            'position. This value should be kept very small (default=3) for '
            'the coarsest step to avoid possible collisions with the '
            'scintillator. If empty (""), the function tries to determine a '
            'sensible set of overshoot values automatically. Lists of steps '
            'must be separated by commas and enclosed in quotes, e.g.: '
            '"3,8,25". (default = %(default)s)'))
    parser.add_argument("-p", "--startposition", type=float, default=0,
        help=('The start position for the search. The focus motion is scanned '
            'in the positive direction starting from this value. '
            '(default = %(default)s)'))
    parser.add_argument("-m", "--maxposition", type=float, default=-1,
        help=('The highest allowed focus positon for the search. If no peak '
            'is found up to this position, the search is aborted. If set to a '
            'negtive value, the high soft limit of the focus motor is used as '
            'the maximum position. (default = %(default)s)'))
    parser.add_argument("-w", "--writeimagestofile", action='store_true',
        default=False,
        help=("Write images to hdf5 file (default = %(default)s)"))

    return parser

if __name__ == "__main__":

    try:
        # tomoalign package is installed in python environment
        import tomoalign.focus as foc
        from tomoalign.utils import get_beamline_config
    except ImportError:
        try:
            # locate the tomoalign package relative to this script's location
            import os
            import sys
            path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
            path = os.path.normpath(os.path.join(path, "../"))
            if not path in sys.path:
                sys.path.append(path)
            import tomoalign.focus as foc
            from tomoalign.utils import get_beamline_config
        except:
            raise EnvironmentError("Could not load the tomoalign package")
    except:
        raise EnvironmentError("Could not load the tomoalign package")

    # quick and dirty fix for Python 2/3 compatibility of getting user input
    try:
        input = raw_input
    except NameError:
        pass

    args = get_argument_parser().parse_args()

    # assign variables from inputs
    step_sizes = args.stepsizes
    overshoot = args.overshoot
    startpos = args.startposition
    maxpos = args.maxposition
    save_image_data = args.writeimagestofile

    if step_sizes == "":
        step_sizes = None
    else:
        try:
            step_sizes = step_sizes.split(',')
            for ind, step in enumerate(step_sizes):
                step_sizes[ind] = np.float(step.strip())
            step_sizes = np.asarray(step_sizes)
        except:
            raise ValueError("Invalid input for stepsizes: {}".format(
                args.stepsizes))

    if overshoot == "":
        overshoot = None
    else:
        try:
            overshoot = overshoot.split(',')
            for ind, step in enumerate(overshoot):
                overshoot[ind] = np.float(step.strip())
            overshoot = np.asarray(overshoot)
        except:
            raise ValueError("Invalid input for overshoot: {}".format(
                args.overshoot))

    if maxpos < 0:
        maxpos = None

    # Let the user know how to set up the beamline
    print("\nStarting the focus search procedure.")
    print(textwrap.dedent('''
        Before running the focus search, please confirm that the experimental
        setup is correctly configured in the "Camera Parameters" panel
        (Launcher > Endstation1 > Camera Parameters).'''))
    print("")
    print("The current settings are:")
    keys=['end_station', 'camera_server', 'camera', 'microscope_name',
          'magnification', 'pixel_size']
    bl_conf = get_beamline_config()
    for key in keys:
        print("  {:20s}: {}".format(key, bl_conf[key]))
    print("")
    print(textwrap.dedent('''
        Please make sure that there is a sample in the beam which produces a
        relatively homogeneous and decent contrast over the camera's field of
        view. Sandpaper is a good focusing sample, for example, or anything
        else that produces pronounced edges or speckle on the detector with
        typical feature sizes of around a few to a few tens of pixels.'''))
    print(textwrap.dedent('''
        Also ensure that all slits along the beamline are opened sufficiently
        to illuminate as much as possible of the detectors field of view and
        that the camera is roughly centered on the X-ray beam.'''))
    input("Press ENTER to start autofocussing.")

    # run the actual focus finding function
    foc.run_find_focus(step_sizes=step_sizes, overshoot=overshoot,
                    start_position=startpos, max_position=maxpos,
                    save_image_data=save_image_data)
