#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to perform an automatic camera alignment (tilt & center).

For more information, display the script's help text

.. code-block:: shell

    auto_align.py -h

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
import signal
import textwrap

from matplotlib import interactive
import matplotlib.pyplot as plt


def get_argument_parser():
    """
    Helper function to create and return the parser object for the command
    line arguments.
    """

    description = textwrap.dedent('''\
        Script to perform an automatic camera alignment (tilt & center).

        The alignment typically needs a few iterations to obtain a perfect
        alignment.

        ''')
    epilog = textwrap.dedent('''\
        EXAMPLES:

        * Perform a completely automatic alignment::

            auto_align.py

        * Perform the alignment to a specified minimum accuracy
          (0.8 pixels for the rotation and 1.0 pixels for the centering)::

            auto_align.py -r 0.8 -c 1.0

        * Limit the maximum number of iterations to 8::

            auto_align.py -i 8

        ''')
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--maxiterations", type=int, default=6,
        help=('The maximum number of iterations before giving up on achieving '
            'the specified alignment accuracy. (default = 6)'))
    parser.add_argument("-r", "--rotationaccuracy", type=float, default=0.25,
        help=('The accuracy to which the camera rotation is to be aligned. '
            'The value specifies the maximum tilt measured in units of pixels '
            'over the larger of the two detector dimensions. '
            '(default = 0.25)'))
    parser.add_argument("-c", "--centeraccuracy", type=float, default=0.5,
        help=('The accuracy, in units of pixels, to which the centering of '
            'the rotation axis with respect to the detector center is to be '
            'aligned. (default = 0.5)'))
    parser.add_argument("-a", "--referenceangle", type=float, default=0.0,
        help=('The reference angle for the alignement images [degrees]. The '
              'first image will be taken at this angle, the second one 180 '
              'degrees from there. (default = 0.0)'))
    parser.add_argument("-f", "--flatfieldPosition", type=float, default=0.0,
        help=('The position at which the flat field image is taken. If set to '
              '0.0, the position will be calculated automatically.'
              '(default = 0.0)'))
    parser.add_argument("-p", "--donotplot", action='store_true',
        default=False,
        help=('If the argument is given, the plotting of the individual '
            'alignment steps is suppressed. (by default plots are shown)'))
    parser.add_argument("-s", "--donotsave", action='store_true',
        default=False,
        help=('If the argument is given, the result file and alignment plots '
            'are not saved to disk (by default results are saved)'))

    return parser

if __name__ == "__main__":

    try:
        # tomoalign package is installed in python environment
        import tomoalign.alignment as align
        from tomoalign.utils import get_beamline_config
    except (ImportError, OSError):
        try:
            # locate the tomoalign package relative to this script's location
            import os
            import sys
            path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
            path = os.path.normpath(os.path.join(path, "../"))
            if not path in sys.path:
                sys.path.append(path)
            import tomoalign.alignment as align
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

    # assign variables from inputs
    args = get_argument_parser().parse_args()
    max_iterations = args.maxiterations
    rot_acc = args.rotationaccuracy
    cen_acc = args.centeraccuracy
    ref_angle = args.referenceangle
    ff_pos = args.flatfieldPosition
    do_plot = not args.donotplot
    do_save = not args.donotsave

    if ff_pos == 0.0:
        sample_out_pos = None
    else:
        sample_out_pos = ff_pos

    # Define an interrupt handler for Ctrl-C which will close all open graphs
    def keyboardInterruptHandler(signal, frame):
        plt.close('all')
        exit(0)
    signal.signal(signal.SIGINT, keyboardInterruptHandler)

    # Let the user know how to set up the beamline
    print("\nStarting the automatic centering and camera alignment "
        "procedure.\n")
    print(textwrap.dedent('''
        Before running the auto alignment, please confirm that the experimental
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
        Please make sure that a suitable sample is mounted. The sample should
        ideally cover the entire vertical extent of the field of view and must
        completely fit into the horizontal field of view. It needs to be pre-
        aligned such that it is completely visible inside the field of view
        when the sample rotation is placed at 0 and 180 degrees.'''))
    print(textwrap.dedent('''
        A long, thin, straight, and vertical wire is ideal as an aligment
        sample.'''))
    print("")
    input("Press ENTER when ready to start the automatic alignment "
        "procedure.\n(or Ctrl-C to quit)\n")

    # start interactive mode for matplotlib
    interactive(True)

    # run the actual focus finding function
    align.run_auto_align(max_iterations=max_iterations,
                        rot_accuracy=rot_acc, cen_accuracy = cen_acc,
                        reference_angle=ref_angle, sample_out_pos=sample_out_pos,
                        plot=do_plot, save_results=do_save)

    # Let the user know how to end the program
    # (more complex due to matplotlib figures)
    print("")
    print("The automatic alignment script has finished.")
    print("To end the program:")
    print("    * Type Ctrl-C in this window and then click on one of the "
          "figures.")
    print("  or")
    print("    * Close all of the open figures manually.")

    # leave the interactive plotting mode and make sure the figures stay open
    interactive(False)
    plt.show()
