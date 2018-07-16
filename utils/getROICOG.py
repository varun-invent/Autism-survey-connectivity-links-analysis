import subprocess
import os
from os.path import join as opj
import nibabel as nib
import numpy as np
from atlasUtility import queryAtlas
from scipy import ndimage
import argparse

# filename = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
# roi = 20


def getGOG(atlas,roi):
    """
    Gives the centre of gravity (MNI coordinates) of an ROI
    Input: Atlas File 1mm, ROI number
    Output: list of MNI coordinates representing Centre of gravity
    Usage:
    >>> atlas= '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
    >>> roi = 20
    >>> print(getGOG(atlas,roi))

    [21.48304821150856, -3.779160186625191, -17.954898911353034]
    """
    brain_data = nib.load(atlas).get_data()
    roi_mask = np.zeros(brain_data.shape)
    roi_mask[np.where(brain_data == roi)] = 1

    CM = ndimage.measurements.center_of_mass(roi_mask)

    MNI = queryAtlas.XYZ2MNI1mm(list(CM))
    # print("Center of Gravity:", MNI)
    return MNI

if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--atlas", required=True,
    	help="Path to 1mm Atlas file")
    ap.add_argument("-r", "--roi", required=True,
    	help="ROI number")
    args = vars(ap.parse_args())


    atlas = args["atlas"]
    roi = int(args["roi"])

    print(getGOG(atlas,roi))







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
