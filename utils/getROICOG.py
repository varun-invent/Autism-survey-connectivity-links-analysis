import subprocess
import os
from os.path import join as opj
import nibabel as nib
import numpy as np
from atlasUtility import queryAtlas
from scipy import ndimage
import argparse
import math

# filename = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
# roi = 20

def _checkPixDim(_atlas):
    """
    Internal Function to nbe used within this script
    Returns the pixel dimension
    """
    if _atlas.header['pixdim'][1] == 2:
        pixdim = 2
    elif _atlas.header['pixdim'][1] == 1:
        pixdim = 1
    else:
        raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1])

    return pixdim

def getGOG(atlas,roi,hemisphere=None):
    """
    Gives the centre of gravity (MNI coordinates) of an ROI
    Input: Atlas File 1mm
           ROI number
           hemisphere = L or R (optional)
    Output: list of MNI coordinates representing Centre of gravity
    Usage:
    >>> atlas= '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
    >>> roi = 20
    >>> print(getGOG(atlas,roi))
    [21.48304821150856, -3.779160186625191, -17.954898911353034]
    """

    brain_img = nib.load(atlas)
    brain_data = brain_img.get_data()

    roi_mask = np.zeros(brain_data.shape)
    roi_mask[np.where(brain_data == roi)] = 1

    size_x = roi_mask.shape[0]

    if hemisphere == 'L':
        # Set the voxes of the ROI on the right hemisphere to zero
        roi_mask[:math.floor(size_x/2),:,:] = 0
    elif hemisphere == 'R':
        # Set the voxes of the ROI on the left hemisphere to zero
        roi_mask[math.floor(size_x/2):,:,:] = 0




    CM = ndimage.measurements.center_of_mass(roi_mask)

    if _checkPixDim(brain_img) == 1:
        MNI = queryAtlas.XYZ2MNI1mm(list(CM))
    elif _checkPixDim(brain_img) == 2:
        MNI = queryAtlas.XYZ2MNI2mm(list(CM))
    # print("Center of Gravity:", MNI)
    return MNI

if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--atlas", required=True,
    	help="Path to 1mm Atlas file")
    ap.add_argument("-r", "--roi", required=True,
    	help="ROI number")
    ap.add_argument("-hem", "--hemisphere", required=False,
    	help="Hemisphere")
    args = vars(ap.parse_args())


    atlas = args["atlas"]
    roi = int(args["roi"])

    if "hemisphere" in args:
        hemisphere = args["hemisphere"]

    print(getGOG(atlas,roi,hemisphere))







# mask = os.path.expandvars('$FSLDIR/data/standard/MNI152_T1_2mm_brain_mask.nii.gz')

# proc = subprocess.Popen(['fslmaths', mask, '-mul', '-1', '-add' ,'1', 'mask_inverted'],
#                          stdout=subprocess.PIPE)
# stdoutdata= proc.communicate()
#
# # To check how the command was executed in cmdline
#
# print("The commandline is: {}".format(subprocess.list2cmdline(proc.args)))
#
# cwd = os.getcwd()
#
# mask_inverted_path = opj(cwd, 'mask_inverted.nii.gz')
