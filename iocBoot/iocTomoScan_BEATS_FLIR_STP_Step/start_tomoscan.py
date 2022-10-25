# This script creates an object of type TomoScan2BM for doing tomography scans at APS beamline 2-BM-A
# To run this script type the following:
#     python -i start_tomoscan_2bm.py
# The -i is needed to keep Python running, otherwise it will create the object and exit
from tomoscan.tomoscan_BEATS_Step import TomoScanBEATS
ts = TomoScanBEATS(["../../db/tomoScan_settings.req",
                    "../../db/tomoScan_step_settings.req",
                  "../../db/tomoScan_BEATS_Step_settings.req"], 
                 {"$(P)":"beats:", "$(R)":"TomoScanStep:"})