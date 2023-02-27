# This script creates an object of type TomoScan_BEATS_FLIR_MICOS_Step for doing tomography scans at BEATS beamline 

from tomoscan.tomoscan_BEATS_FLIR_MICOS_Step import TomoScanBEATSFlirMicosStep
ts = TomoScanBEATSFlirMicosStep("../../configurations/pvlist.json",["../../db/tomoScan_settings.req", "../../db/tomoScan_BEATS_FLIR_MICOS_Step_settings.req"], {"$(P)":"tomoscanBEATS:", "$(R)":"FlirMicosStep:"})
