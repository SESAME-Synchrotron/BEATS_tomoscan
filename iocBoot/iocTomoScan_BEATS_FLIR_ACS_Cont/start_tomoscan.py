# This script creates an object of type TomoScan_BEATS_FLIR_ACS_Cont for doing tomography scans at BEATS beamline 

from tomoscan.tomoscan_BEATS_FLIR_ACS_Cont import TomoScanBEATSFlirAcsCont
ts = TomoScanBEATSFlirAcsCont("../../configurations/pvlist.json",["../../db/tomoScan_settings.req", "../../db/tomoScan_BEATS_FLIR_ACS_Cont_settings.req"], {"$(P)":"tomoscanBEATS:", "$(R)":"FlirAcsCont:"})
