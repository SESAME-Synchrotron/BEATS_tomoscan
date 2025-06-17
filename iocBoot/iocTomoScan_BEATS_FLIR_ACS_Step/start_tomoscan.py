# This script creates an object of type TomoScan_BEATS_FLIR_ACS_Step for doing tomography scans at BEATS beamline 

from tomoscan.tomoscan_BEATS_FLIR_ACS_Step import TomoScanBEATSFlirAcsStep
ts = TomoScanBEATSFlirAcsStep("../../configurations/pvlist.json",["../../db/tomoScan_settings.req", "../../db/tomoScan_BEATS_FLIR_ACS_Step_settings.req"], {"$(P)":"tomoscanBEATS:", "$(R)":"FlirAcsStep:"})
