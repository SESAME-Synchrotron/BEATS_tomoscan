Introduction to TomoAlign
=========================

The TomoAlign package provides several classes, functions and scripts to perform various alignment tasks for tomographic microscopy measurements at the TOMCAT beamline X02DA of the Swiss Light Source.

As such, the code is quite specific to the available hardware at the TOMCAT beamline, but the concepts may be easily adapted to other situations.

Currently, the following alignment procedures are supported:

* Automatic focusing of the microscope / camera image and calculation of the
  scintillator tilt with instructions on how to correct the tilt (see
  :ref:`focus:Focusing the camera`).
* Automatic centering of the rotation axis position with respect to the center
  of the detector's field of view (see :ref:`alignment:Alignment: Camera tilt
  and rotation axis centering`)
* Automatic alignment of the camera's rotation axis to align the rotation axis
  direction with the direction of the pixel columns (see
  :ref:`alignment:Alignment: Camera tilt and rotation axis centering`).
* Coming soon: Automatic alignment of the sample holder pitch with respect to
  the incoming X-ray beam direction to make sure the rotation axis is perfectly
  perpendicular to the beam. (see :ref:`sample_pitch:Alignment: Sample pitch`)
