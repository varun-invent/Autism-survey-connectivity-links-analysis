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

def getCOG(atlas,roi,hemisphere=None):
    """
    Gives the centre of gravity (MNI coordinates) of an ROI
    Input: Atlas File 1mm
           ROI number
           hemisphere = L or R (optional)
    Output: list of MNI coordinates representing Centre of gravity
    Usage:
    >>> atlas= '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
    >>> roi = 20
    >>> print(getCOG(atlas,roi))
    [21.48304821150856, -3.779160186625191, -17.954898911353034]
    """

    brain_img = nib.load(atlas)
    brain_data = brain_img.get_data()

    if len(brain_data.shape) == 3: # 3D brain file
        roi_mask = np.zeros(brain_data.shape)
        roi_mask[np.where(brain_data == roi)] = 1
    else: # 4D Brain File
        roi_mask = np.zeros(tuple(brain_data.shape[:3]))
        roi_mask = brain_data[:,:,:,roi]



    # roi_mask = np.zeros(brain_data.shape)
    # roi_mask[np.where(brain_data == roi)] = 1

    size_x = roi_mask.shape[0]

    if hemisphere == 'L':
        # Set the voxes of the ROI on the right hemisphere to zero
        roi_mask[:math.floor(size_x/2),:,:] = 0
    elif hemisphere == 'R':
        # Set the voxes of the ROI on the left hemisphere to zero
        roi_mask[math.floor(size_x/2):,:,:] = 0



    if len(brain_data.shape) == 3: # 3D brain file
        CM = ndimage.measurements.center_of_mass(roi_mask)
        MNI = _XYZ2MNI(brain_img,CM)
    else: # 4D Brain File
        highest_prob_idx = np.where(roi_mask == np.max(roi_mask))
        MNI = []
        peak_list = []
        CM = ndimage.measurements.center_of_mass(roi_mask)
        dist = float(np.inf)
        # The loop finds the peak coordinate closest to the COG
        for i in range(len(highest_prob_idx[0])):
            peak = [highest_prob_idx[0][i],highest_prob_idx[1][i],highest_prob_idx[2][i]]
            # Find the peak closest to the COG
            current_dist = abs(CM[0]-peak[0]) + abs(CM[1]-peak[1]) + abs(CM[1]-peak[1])
            if current_dist < dist:
                if len(peak_list) != 0:
                    peak_list = []
                peak_list.append(peak)
                dist = current_dist
            elif current_dist == dist:
                peak_list.append(peak)
                dist = current_dist
            else:
                pass

        # The above 'For loop' might result in miltiple peak coordinates (peak list) having same distance from COG
        # Check which of the peak list has least x coordinate i.e closest to midline (My heuristic) to select one peak
        x = float(np.inf)
        res = []
        for coordinates in peak_list:
             current_x = abs(coordinates[0])
             if current_x < x:
                 res = []
                 res.append(coordinates)
             elif current_x == x:
                 res.append(coordinates)
             else:
                 pass


        # Find the
        MNI = []
        for res_peak in res:
            MNI.append(_XYZ2MNI(brain_img,res_peak))

    return MNI


def _XYZ2MNI(brain_img,CM):
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

    print(getCOG(atlas,roi,hemisphere))
