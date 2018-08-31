# import sys
# import os
#
# # Using https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python
# utils_path = os.path.abspath("utils")
#
# # Using https://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168
# sys.path.insert(0, utils_path)


import numpy as np
from scipy.ndimage.measurements import label as lb
import nibabel as nib
from utils import getROICOG
from atlasUtility import queryAtlas

"""
This tool will take as input the brain map - a 3D file and an atlas name.
User can set a threshold for example <1.3 to 2.5>
    Program finds clusters.
    For each cluster:
        Finds the span of cluster
        Check how many ROIs are covered by the cluster.
        For each ROI covered
        Find the number and percentage of voxels it covers and reports the peak coordinate closest to COG of the voxels in that ROI.
        Also gives the name and coordinates of the peak coordinate of the cluster.

"""

beg = 0.2
end = 1.0

positive_range = [beg,end]
negative_range = [-beg, -end]

in_brain_file = '/media/varun/LENOVO5/BackupDhyanam/fdr_and_results/motionRegress1filt1global0smoothing1_eyes_closed/map_logq.nii.gz'
in_atlas_file = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/aalAtlas/AAL.nii.gz'

# Read Brain file:
brain = nib.load(in_brain_file).get_data()[:,:,:,0]
# Read Atlas file
atlas = nib.load(in_atlas_file).get_data()

# Brain_zero is used later to calculate the center of gravity of the cluster
# voxels overlapping with atlas voxels
brain_zero = np.zeros(brain.shape)



# Apply thresholding
brain[(brain < -end) | (brain > -beg) | (brain < beg) | (brain > end)] = 0

# Find clusters
clusters, num_clusters = lb(brain)

for cluster_number in range(1,num_clusters + 1):
    # Coordinates that are present in cluster given by cluster_number
    cluster_indices = np.where(clusters == cluster_number)

    # Find the atlas labels/regions that the cluster spans
    atlas_regions_labels = np.unique(atlas[cluster_indices])
    print(atlas_regions_labels)

    # iterate over all the labes/regions
    for label in atlas_regions_labels:
        # Find all the coordinates of these labels

        # Skipping the Label 0
        if label == 0:
            continue

        atlas_label_indices = np.where(atlas == label)

        """ Find the cluster coordinates overlapping the label/region
        under consideration """

        # Changing the form of cluster indices to (x,y,z) tuple
        cluster_indices_tuple_list = []
        cluster_indices_zip = zip(cluster_indices[0], cluster_indices[1], cluster_indices[2])
        for coordinates in cluster_indices_zip:
            cluster_indices_tuple_list.append(coordinates)

        # Changing the form of atlas indices to (x,y,z) tuple
        atlas_label_indices_tuple_list = []
        atlas_label_indices_zip = zip(atlas_label_indices[0], atlas_label_indices[1], atlas_label_indices[2])
        for coordinates in atlas_label_indices_zip:
            atlas_label_indices_tuple_list.append(coordinates)

        # 1. Find intersecion of the above two lists
        overlapping_coordinates = list(set(cluster_indices_tuple_list).intersection(set(atlas_label_indices_tuple_list)))

        # 2. Make an brain array and initialize the overlapping coordinates with the values from brain

        # Transform coordinates list to list of indices as returned by np.where()
        # Ref: https://stackoverflow.com/questions/12974474/how-to-unzip-a-list-of-tuples-into-individual-lists
        overlapping_indices =  zip(*overlapping_coordinates)

        brain_zero[overlapping_indices] = brain[overlapping_indices]

        # 3. Then use the already created functions to do the following:
            # a. Find the representative coordinate of the intersection

        # Create a dummy atlas with just one region abd label that as 1
        #  Ref: https://stackoverflow.com/questions/32322281/numpy-matrix-binarization-using-only-one-expression
        overlap_region_so_called_atlas = np.where(brain_zero > 0, 1, 0)
        peak_cog_obj = roicog.getROICOG(overlap_region_so_called_atlas)

        #  roi = 1 is used as parameter in the following statement
        representative_coordinate = peak_cog_obj.getCOG(1)


            # b. Also report the MNI coordinate
            # c. Report the name of the region
            # d. Number and Percentage of voxels overlapping the region
            # e. Peak coordinate of the cluster
            # f. COG weighted by peak  which is the representative_coordinate alreaded computed
