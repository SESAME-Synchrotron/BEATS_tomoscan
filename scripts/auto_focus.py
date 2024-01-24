#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to automatically focus the microscope/camera setup at TOMCAT.

For more information, display the script's help text

.. code-block:: shell

    auto_focus.py -h

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

    description = textwrap.dedent('''
        Script to automatically focus the microscope/camera setup at TOMCAT.

        The autofocus operation must be started close to the actual focus
        position such that the true focus position lies within the specified
        search range.

        ''')
    epilog = textwrap.dedent('''
        EXAMPLES:

        * Run a completely automatic autofocussing procedure::

            auto_focus.py

        * Run an autofocussing procedure with a specified step size of 0.5
          microns over a range of +/- 35 microns around the start position at
          2430 um::

            auto_focus.py -s 0.5 -r 35 -p 2430

        ''')
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--stepsize", type=float, default=-1.0,
        help=('The step size to use in the search, given in microns. If '
            'ommitted or set to a negative number, the search step is '
            'determined automatically based on the effective pixel size. '
            '(default = %(default)s)'))
    parser.add_argument("-r", "--range", type=float, default=-1.0,
        help=('The half-width of the range within which the focus position is '
            'searched, given in microns. I.e.: a value of range=25 will '
            'perform a search within a window of (+/-) 25 um from the start '
            'position. If ommitted or set to a negative number, the search '
            'range is determined automatically based on the effective pixel '
            'size. (default = %(default)s)'))
    parser.add_argument("-p", "--startposition", type=float, default=-1.0,
        help=('The start position for the autofocus run. The best focus must '
            'be within a window with half-width of `range` around this '
            'position. If ommitted or set to a negative number, the search '
            'will be performed around the current position. '
            '(default = %(default)s)'))
    parser.add_argument("-x", "--pixelsize", type=float, default=-1.0,
        help=('The effective pixel size of the image in microns. If ommitted '
            'or set to a negative number, the pixel size is taken from the '
            'current beamline configuration. This option can be used to '
            'override that value if the true pixel size is different for some '
            'reason. (default = %(default)s)'))
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
    step_size = args.stepsize
    search_range = args.range
    startpos = args.startposition
    pixel_size = args.pixelsize
    save_image_data = args.writeimagestofile

    if step_size <= 0:
        step_size = None
    if search_range <= 0:
        search_range = None
    if startpos <= 0:
        startpos = None
    if pixel_size <= 0:
        pixel_size = None

    # Let the user know how to set up the beamline
    print("\nStarting the autofocus procedure.")
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
    input("Press ENTER to start autofocussing.\n(or Ctrl-C to quit)\n")

    # run the actual focus finding function
    foc.run_auto_focus(search_range=search_range, search_step=step_size,
                    start_position=startpos, pixel_size=pixel_size,
                    save_image_data=save_image_data)
