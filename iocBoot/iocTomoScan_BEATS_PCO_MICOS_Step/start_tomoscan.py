# This script creates an object of type TomoScan_BEATS_PCO_MICOS_Step for doing tomography scans at BEATS beamline 

from tomoscan.tomoscan_BEATS_PCO_MICOS_Step import TomoScanBEATSPcoMicosStep
ts = TomoScanBEATSPcoMicosStep("../../configurations/pvlist.json", ["../../db/tomoScan_settings.req", "../../db/tomoScan_BEATS_PCO_MICOS_Step_settings.req"], {"$(P)":"tomoscanBEATS:", "$(R)":"PcoMicosStep:"})
