import sys
import os

"""
The folowing script goes through the AAL atlas index locations and finds the COG
for each of the region and check if it lies inside the region or not.
"""

# Using https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python
utils_path = os.path.abspath("utils")

# Using https://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168
sys.path.insert(0, utils_path)

import getROICOG as roicog
from atlasUtility import queryAtlas
import nibabel as nib

AALROIindex = ["2001","2002","2101","2102","2111","2112","2201","2202","2211","2212","2301","2302","2311","2312","2321","2322","2331","2332","2401","2402","2501","2502","2601","2602",\
"2611","2612","2701","2702","3001","3002","4001","4002","4011","4012","4021","4022","4101","4102","4111","4112","4201","4202","5001","5002","5011","5012","5021","5022","5101",\
"5102","5201","5202","5301","5302","5401","5402","6001","6002","6101","6102","6201","6202","6211","6212","6221","6222","6301","6302","6401","6402","7001","7002","7011","7012",\
"7021","7022","7101","7102","8101","8102","8111","8112","8121","8122","8201","8202","8211","8212","8301","8302","9001","9002","9011","9012","9021","9022","9031","9032","9041",\
"9042","9051","9052","9061","9062","9071","9072","9081","9082","9100","9110","9120","9130","9140","9150","9160","9170"]


atlas = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/aalAtlas/AAL.nii'

brain = nib.load(atlas).get_data()

obj = roicog.getROICOG(atlas)

for roi in AALROIindex:
    COG = obj.getCOG(int(roi))
    print('Index %s : %s'%(roi, COG ))
    XYZ = queryAtlas.MNI2XYZ2mm(COG)
    if brain[XYZ[0],XYZ[1],XYZ[2]] != int(roi):
        print('COG Lies outside for ROI Index %s'%roi)
