import numpy as np
from scipy.ndimage.measurements import label as lb
import nibabel as nib

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

beg = 1.3
end = 2.5
positive_range = [beg,end]
negative_range = [-beg, -end]

in_brain_file = '/media/varun/LENOVO5/BackupDhyanam/fdr_and_results/motionRegress1filt1global0smoothing1_eyes_closed/map_logq.nii.gz'
in_atlas_file = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/aalAtlas/AAL.nii.gz'

# Read Brain file:
brain = nib.load(in_brain_file).get_data()
# Read Atlas file
atlas = nib.load(in_atlas_file).get_data()


# Apply thresholding
brain[np.where((brain < -end) & (brain > -beg) & (brain < beg) & (brain > end))] = 0

# Find clusters
clusters, num_clusters = lb(brain)

for cluster_number in range(1,num_clusters + 1):
    cluster_indices = np.where(brain == cluster_number)
    atlas_labels = np.unique(atlas[cluster_indices])
