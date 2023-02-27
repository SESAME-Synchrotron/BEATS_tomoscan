# This script creates an object of type TomoScan_BEATS_PCO_MICOS_Cont for doing tomography scans at BEATS beamline 

from tomoscan.tomoscan_BEATS_PCO_MICOS_Cont import TomoScanBEATSPcoMicosCont
ts = TomoScanBEATSPcoMicosCont("../../configurations/pvlist.json", ["../../db/tomoScan_settings.req", "../../db/tomoScan_BEATS_PCO_MICOS_Cont_settings.req"], {"$(P)":"tomoscanBEATS:", "$(R)":"PcoMicosCont:"})

