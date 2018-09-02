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
from scipy.ndimage.measurements import center_of_mass as com
import nibabel as nib
# from utils import getROICOG
from utils.atlasUtility import queryAtlas
import argparse

class cluster_reporting_tool:
    """
    This tool will take as input the brain map - a 3D file and an atlas name.
    User can set a threshold for example <1.3>
        Program finds clusters.
        For each cluster:
            Finds the span of cluster
            Check how many ROIs are covered by the cluster.
            For each ROI covered
            Find the number and percentage of voxels it covers and reports the
                      peak coordinate closest to COG of the voxels in that ROI.
            Also gives the name and coordinates of the peak coordinate of the
                                                                       cluster.

    """
    def __init__(self, contrast, atlas, threshold, volume = 0):
        # Read Brain file:
        self.brain = nib.load(contrast).get_data()
        self.brain[np.isnan(self.brain)] = 0
        # Read Atlas file
        self.atlas = nib.load(atlas).get_data()

        self.thresh = threshold

        self.volume = volume

    def getNearestVoxel(self, roi_mask, COG):
        # roi_mask = np.zeros(atlas.shape)
        # roi_mask[np.where(atlas == roi)] = 1
        roiCoord = np.where(roi_mask != 0)

        peak_list = []
        dist = float(np.inf)
        for [x, y, z] in zip(roiCoord[0], roiCoord[1], roiCoord[2]):
            peak = [x, y, z]
            current_dist = abs(x - COG[0]) + abs(y - COG[1]) + abs(z - COG[2])
            if current_dist < dist:
                if len(peak_list) != 0:
                    peak_list = []
                peak_list.append(peak)
                dist = current_dist
            elif current_dist == dist:
                peak_list.append(peak)
                dist = current_dist

        # The above 'For loop' might result in miltiple peak coordinates(peak list)
        # having same distance from COG Check which of the peak list has least
        # x coordinate i.e closest to midline (My heuristic) to select one peak

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

        # # Find the MNI coordinates of the peak coordinates
        # MNI = []
        # for res_peak in res:
        #     MNI.append(queryAtlas.XYZ2MNI2mm(res_peak))
        #
        # return MNI

        if len(res) > 1:
            raise Exception('Multiple candidates for Representative \
            coordinates. Please report to the author of the tool about this!')

        return res[0]


    def report(self, volume = None, threshold = None):
        # To take care if user has given a 4D contrast
        if volume != None:
            self.volume = volume

        if len(self.brain.shape) > 3:
            brain = np.array(self.brain[:,:,:,self.volume])
        else:
            brain = np.array(self.brain)

        if threshold != None:
            self.thresh = threshold


        """
        Brain_zero is used later to calculate the center of gravity of the
        cluster voxels overlapping with atlas voxels
        """

        brain_zero = np.zeros(brain.shape)

        # Apply thresholding
        brain[(brain < self.thresh) & (brain > -self.thresh)] = 0

        # Find clusters
        clusters, num_clusters = lb(brain)

        for cluster_number in range(1,num_clusters + 1):
            # Coordinates that are present in cluster given by cluster_number
            cluster_indices = np.where(clusters == cluster_number)

            # Find the atlas labels/regions that the cluster spans
            atlas_regions_labels = np.unique(self.atlas[cluster_indices])
            # print(atlas_regions_labels)

            # iterate over all the labes/regions
            for label in atlas_regions_labels:
                # Find all the coordinates of these labels

                # Skipping the Label 0
                if label == 0:
                    continue

                atlas_label_indices = np.where(self.atlas == label)

                """ Find the cluster coordinates overlapping the label/region
                under consideration """

                # Changing the form of cluster indices to (x,y,z) tuple
                # cluster_indices_tuple_list = []
                cluster_indices_zip = zip(cluster_indices[0], cluster_indices[1]
                                      , cluster_indices[2])
                # for coordinates in cluster_indices_zip:
                #     cluster_indices_tuple_list.append(coordinates)

                cluster_indices_tuple_list = list(cluster_indices_zip)

                # Changing the form of atlas indices to (x,y,z) tuple
                # atlas_label_indices_tuple_list = []

                atlas_label_indices_zip = \
                zip(atlas_label_indices[0], atlas_label_indices[1],
                                            atlas_label_indices[2])

                # for coordinates in atlas_label_indices_zip:
                #     atlas_label_indices_tuple_list.append(coordinates)

                atlas_label_indices_tuple_list = list(atlas_label_indices_zip)

                # 1. Find intersecion of the above two lists
                overlapping_coordinates = \
                list(set(cluster_indices_tuple_list).intersection(
                                           set(atlas_label_indices_tuple_list)))

                """
                2. Make an brain array and initialize the overlapping
                coordinates with the values from brain

                # Transform coordinates list to list of indices as
                returned by np.where()
                # Ref: https://stackoverflow.com/questions/12974474/
                how-to-unzip-a-list-of-tuples-into-individual-lists

                """
                overlapping_indices_zip =  zip(*overlapping_coordinates)
                # overlapping_indices_tuple_list = []
                # for ind_list in overlapping_indices_zip:
                #     overlapping_indices_tuple_list.append(ind_list)

                overlapping_indices_tuple_list = list(overlapping_indices_zip)


                brain_zero[overlapping_indices_tuple_list] = \
                                           brain[overlapping_indices_tuple_list]

                """
                3. Then use the already created functions to do the following:
                    a. Find the representative coordinate of the intersection

                Create a dummy atlas (roi_mask) with just one region and label
                that as 1

                Ref: https://stackoverflow.com/questions/32322281/
                numpy-matrix-binarization-using-only-one-expression
                """

                roi_mask_for_unweighted_cog = np.where(brain_zero != 0, 1, 0)
                roi_mask_for_weighted_cog = brain_zero


                cog_unweighted = com(roi_mask_for_unweighted_cog)
                cog_weighted = com(roi_mask_for_weighted_cog)



                if not roi_mask_for_unweighted_cog[cog_unweighted]:
                    cog_unweighted = \
                              self.getNearestVoxel(roi_mask_for_unweighted_cog,
                                                   cog_unweighted)

                if not roi_mask_for_weighted_cog[cog_weighted]:
                    cog_weighted= \
                              self.getNearestVoxel(roi_mask_for_weighted_cog,
                                                   cog_weighted)

               print('COM Weighted', cog_weighted)
               print('COM Unweighted', cog_unweighted)


               


                # MNI = self._XYZ2MNI(CM)

                pass

                brain_zero.fill(0)

                    # b. Also report the MNI coordinate
                    # c. Report the name of the region
                    # d. Number and Percentage of voxels overlapping the region
                    # e. Peak coordinate of the cluster
                    # f. COG weighted by peak  which is the representative_coordinate alreaded computed


if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--contrast", required=False,
                    help="Path to contrast file")
    ap.add_argument("-a", "--atlas", required=False,
                    help="Path to Atlas file")
    ap.add_argument("-t", "--thresh", required=False,
                    help="Threshold")
    ap.add_argument("-v", "--vol", required=False,
                    help="Volume Number (If a 4D contrast is used as input) \
                    [Starts from 1]")


    args = vars(ap.parse_args())

    if args["contrast"] != None:
        contrast = args["contrast"]
    else:
        contrast = '/media/varun/LENOVO5/BackupDhyanam/fdr_and_results/' + \
        'motionRegress1filt1global0smoothing1_eyes_closed/map_logp.nii.gz'
        contrast = 'map_logq_2mm.nii.gz'
    print('Using contrast %s' % contrast)

    if args["atlas"] != None:
        atlas = args["atlas"]
    else:
        atlas = '/home/varun/Projects/fmri/' + \
        'Autism-survey-connectivity-links-analysis/aalAtlas/AAL.nii.gz'
    print("Using atlas %s" % atlas)

    if args["thresh"] != None:
        threshold = float(args["thresh"])
    else:
        threshold = 1.3

    print("Using threshold of %s" % threshold)

    if args["vol"] != None:
        volume = int(args["vol"])
    else:
        volume = 0

    print("Using Volume_index %s" % str(volume))





    crl_obj = cluster_reporting_tool(contrast, atlas, threshold, volume)
    crl_obj.report()
