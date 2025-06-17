# This script creates an object of type TomoScan_BEATS_PCO_ACS_Step for doing tomography scans at BEATS beamline 

from tomoscan.tomoscan_BEATS_PCO_ACS_Step import TomoScanBEATSPcoAcsStep
ts = TomoScanBEATSPcoAcsStep("../../configurations/pvlist.json", ["../../db/tomoScan_settings.req", "../../db/tomoScan_BEATS_PCO_ACS_Step_settings.req"], {"$(P)":"tomoscanBEATS:", "$(R)":"PcoAcsStep:"})
