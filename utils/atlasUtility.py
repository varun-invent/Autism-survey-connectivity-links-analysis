# coding: utf-8

import pandas as pd
import nibabel as nib
import numpy as np
import math
import xml.etree.ElementTree as ET
from tqdm import tqdm


# In[66]:


# Improved
class queryAtlas:
    '''
    atlasPaths : List of paths to the nii files to be considered in order of preference
    atlasLabelsPaths : List of paths to the xml files containing labels to be considered in order of preference
    coord : List [x,y,z] of MNI coordinates
    Usage:
    >>> atlasPaths1  = ['hoAtlas/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz',\
               'hoAtlas/HarvardOxford-sub-maxprob-thr25-2mm.nii.gz',
               'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz']
    >>> atlasLabelsPaths1 = ['hoAtlas/HarvardOxford-Cortical.xml','hoAtlas/HarvardOxford-Subcortical.xml',\
                    'cerebellumAtlas/Cerebellum_MNIflirt.xml']
    >>> q1 = queryAtlas(atlasPaths1,atlasLabelsPaths1)
    >>> q1.getAtlasRegions([-6,62,-2])
    (1, 'Frontal Pole', 0)

    Also, this function supports the use of 4D probability map of the atlas to find the nearby
    maximim probability region in the vicinity of 3 voxel cube if the region at a particular voxel is not
    present in the atlas.
    Set prob = True  and provide a 4D nii.gz file path as atlas_path



    '''
    def __init__(self,atlasPaths,atlasLabelsPaths, prob = False):
        self.atlasPaths = atlasPaths
        self.atlasLabelsPaths = atlasLabelsPaths
        self.prob = prob
        self.itr = [0,1,-1,2,-2,3,-3] # represents the neighbourhood to search the queryVoxel
        self.atlas_list = []
        self.pixdim_list = []

        for index,atlasPath in enumerate(self.atlasPaths):

            _atlas = nib.load(atlasPath)
            atlas = _atlas.get_data()

            self.atlas_list.append(atlas)


            print('Atlas read')
            if _atlas.header['pixdim'][1] == 2:
                pixdim = 2
    #             x,y,z = self.MNI2XYZ2mm(coordMni)
            elif _atlas.header['pixdim'][1] == 1:
                pixdim = 1
    #             x,y,z = self.MNI2XYZ1mm(coordMni)
            else:
                raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )

            self.pixdim_list.append(pixdim)
            print('checked Pixel dimension')



    def MNI2XYZ1mm(self, mni):
        """
        Converts the given MNI coordinates to X,Y,Z cartesian coordinates corresponding to the 1mm atlas
        """
        x =  - mni[0] + 90
        y = mni[1] + 126
        z = mni[2] + 72
        return [x,y,z]

    def MNI2XYZ2mm(self, mni):
        """
        Converts the given MNI coordinates to X,Y,Z cartesian coordinates corresponding to the 2mm atlas
        """
        x =  math.floor((- mni[0] + 90)/2.0)
        y = math.floor((mni[1] + 126)/2.0)
        z = math.floor((mni[2] + 72)/2.0)
        return [x,y,z]

    def XYZ2MNI1mm(self, xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 1mm atlas
        """
        mni_x = - xyz[0] + 90
        mni_y = xyz[1] - 126
        mni_z = xyz[2] -72
        return [mni_x, mni_y, mni_z]


    def XYZ2MNI2mm(self, xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 2mm atlas
        """
        mni_x = - 2*xyz[0] + 90
        mni_y = 2*xyz[1] - 126
        mni_z = 2*xyz[2] -72
        return [mni_x, mni_y, mni_z]

    def roiName(self, atlasLabelsPath, roiNum):
        '''
        Takes as input the Atlas labels path and ROI Number and outputs the ROI name for that atlas
        '''
        atlasDict = {}
        root = ET.parse(atlasLabelsPath).getroot()
        elem = root.find('data')
        for regionRow in elem.getchildren():
            # roiNumber  = int(regionRow.items()[2][1]) + 1 .items() gives the items in arbitary order so indexing changes
            roiNumber = int(regionRow.get(key='index')) + 1
            roiName = regionRow.text
            atlasDict[roiNumber] = roiName

        return atlasDict[roiNum]

    def getAtlasRegions(self, coordMni):
        '''
        Takes as input MNI coordinates and returns a tuple (ROI_number, Region_name, Atlas_index_used)

        Algorithm:
        Loops over multiple atlases
            For each atlas get the maximum probability regions (2 here)
            Select the max prob region with its increment vector which will be used later to calculate the distance
            of each voxel fromt the query voxel.
            Discard the first one if it is WM or Cerebral cortex and select the second if it is not WW or CCortex.
            Save the [roiNumber, roiName ,final_coord ,final_itr, max_prob, index(representing atlas)] in an 'out' list
            (Traverse this list to find the closest max probabiliy region across atlases)
        Loop over the 'out' list
            select the atlases that contain the closest regions
        Loop over those regions to find the max probability region
        return roiNumber, roiName, atlasIndex

        '''
        roiNumber = None
        roiName = None


        atlasIndex = 0
        # Enumerates over all the given atlases and stops when the region is found in some atlas.

#         global_roiNumber = None
#         global_final_coord = None
#         global_final_itr = None
#         global_max_prob = 0
#         global_max_prob_index = 0

        _roiNumber, _final_coord, _final_itr, _max_prob = None, None, None, None

        out = []
        for index,atlasPath in enumerate(self.atlasPaths):

            if roiNumber == None or self.prob == True:
#                 _atlas = nib.load(atlasPath)
#                 atlas = _atlas.get_data()
#                 if _atlas.header['pixdim'][1] == 2:
                if self.pixdim_list[index] == 2:
                    x,y,z = self.MNI2XYZ2mm(coordMni)
#                 elif _atlas.header['pixdim'][1] == 1:
                elif self.pixdim_list[index] == 1:
                    x,y,z = self.MNI2XYZ1mm(coordMni)
                else:
                    raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )


#                 roiNumber = atlas[x,y,z]
                if self.prob == False:
                    roiNumber = self.atlas_list[index][x,y,z]
                else:
#                     vec_of_prob = self.atlas_list[index][x,y,z,:]
#                     roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
#                     max_prob =  vec_of_prob[roiNumber]
#                     if max_prob == 0: # # Coordinate is outside the atlas

                    _roiNumber, _final_coord, _final_itr, _max_prob = self.get_neighbouring_coordinates(x,y,z,self.itr,index, largest= 2)

                    # Getting the Highest probability region
                    if len(_roiNumber) == 0:
                        continue

                    roiNumber=_roiNumber[0]
                    final_coord=_final_coord[0]
                    final_itr=_final_itr[0]
                    max_prob=_max_prob[0]



#                 print('ROI Number',roiNumber)
                if roiNumber != 0:
                    roiName = self.roiName(self.atlasLabelsPaths[index], roiNumber)

                    roiName  = roiName.strip()

                    if self.prob == True:

                        if roiName == 'Right Cerebral White Matter' or roiName == 'Left Cerebral White Matter'\
                        or roiName == 'Left Cerebral Cortex' or roiName == 'Right Cerebral Cortex':
                            # Look for second largest in the same atlas
                            if len(_roiNumber) > 1: # If second highest prob region exists
                                # Getting the second Highest probability region
                                roiNumber=_roiNumber[1]
                                final_coord=_final_coord[1]
                                final_itr=_final_itr[1]
                                max_prob=_max_prob[1]
                                roiName = self.roiName(self.atlasLabelsPaths[index], roiNumber)
                                roiName  = roiName.strip()
                                if roiName == 'Right Cerebral White Matter' or roiName == 'Left Cerebral White Matter'\
                        or roiName == 'Left Cerebral Cortex' or roiName == 'Right Cerebral Cortex':
                                    continue # when both of the top 2 pics are irrelevant to us




                            else:
    #                                 roiNumber = None
    #                                 atlasIndex = atlasIndex + 1
                                continue

    #                         if global_max_prob < max_prob:
    #                             global_max_prob_index = atlasIndex
    #                             global_max_prob = max_prob

                        out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])


                    else:
                        if roiName == 'Right Cerebral White Matter' or roiName == 'Left Cerebral White Matter'\
                        or roiName == 'Left Cerebral Cortex' or roiName == 'Right Cerebral Cortex':
                            roiNumber = None
                            atlasIndex = atlasIndex + 1
                            continue




                else:
                    roiNumber = None
                    atlasIndex = atlasIndex + 1

#         print('OUT:',out)

        """
        Loop over the 'out' list
            select the atlases that contain the closest regions
        Loop over those regions to find the max probability region

        """
        if self.prob == True: # To find the minimum distance among all the arrays
            final_output_idx = 0
            final_min_dist = float('Inf')
            for idx,output in enumerate(out):

                dist = abs(output[3][0]) + abs(output[3][1]) + abs(output[3][2])
                if final_min_dist > dist:
#                     final_output_idx = idx
                    final_min_dist = dist

            final_max_prob = 0
            for idx,output in enumerate(out): # To find the max probability if there are multiple min arrays dist
                dist = abs(output[3][0]) + abs(output[3][1]) + abs(output[3][2])
#                 print('Dist and final min dist',dist, final_min_dist)
                if dist == final_min_dist:
                    if final_max_prob < output[4]:
                        final_max_prob = output[4]
                        final_output_idx = idx

#             print('final_output_idx',final_output_idx)


            if len(out) == 0:
                roiNumber, roiName, atlasIndex = 0, None, None
            else:
                roiNumber, roiName, atlasIndex = out[final_output_idx][0], out[final_output_idx][1], out[final_output_idx][5]


        if self.prob == False:
            if roiNumber == None:
                roiNumber, roiName, atlasIndex = 0, None, None

        return int(roiNumber), roiName, atlasIndex


    def get_neighbouring_coordinates(self,x,y,z, itr, atlas_index, largest=1):
        """
        Takes X,Y,Z brain coordinates in image space and finds the region according to the given atlas.
        Using the max(itr) number of voxels cube arounf the query voxel, it tries to find the most
        appropriate region according to the following criteria:

        The top 'largest' largest regions are extracted for each atlas at the given voxel.
        If the given voxel doesnot have any information in the atlas, then the nearby voxels are looked for region
        information. The result is the nearest voxel's region. The nearest voxel is found by employing a distance
        metric given by `dist = abs(xi) +  abs(yi)  + abs(zi)` where xi,yi,zi is the increments in the location of
        the neighbourhood of the voxel under query.

        Inputs:

        Outputs:
        final_roi_list: The top 2 ROI numbers
        final_coord_list: Corresponding MNI Coordinates given as a list of lists
            [[MNI_coordinates1],[MNI_coordinates2]]
        final_itr_list: List of increments to reach at the target voxel
        final_max_prob_list: List if probabilities of the corresponding regions selected

        Algorithm: (for prob = True)
        Loop over all voxel increments
            Loop over how many largest regions are needed
                Get the max region corresponding to the given voxel
                    If the max region lies inside the atlas
                        Make sure we are not far from the region we have already found (i.e. pritorizing over
                        the diatance feom the quesry voxel over the probability of the neighbouring voxels).
                            Populate the roi_list.
                        if roi_list is not empty
                            Pupulate the final_roi_list with the above got ROI_list
                            Similarly populate the other final lists


        """
        final_coord = [x,y,z]
        old_dist = float('Inf')
        final_itr = [0,0,0]
        final_roi = 0


        final_roi_list = []
        final_coord_list = []
        final_itr_list = []
        final_max_prob_list = []


        roi_list = []
        coord_list = []
        itr_list = []
        max_prob_list = []


        for xi in itr:
            for yi in itr:
                for zi in itr:
                    roi_list = []
                    coord_list = []
                    itr_list = []
                    max_prob_list = []
                    vec_of_prob = np.array(self.atlas_list[atlas_index][x-xi,y-yi,z-zi,:])
                    for counter in range(largest):

                        roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
                        max_prob =  vec_of_prob[roiNumber - 1]
    #                     print('coord',x-xi,y-yi,z-zi)
    #                     print('MAx_prob',max_prob)
                        if max_prob != 0: # the max roi lies inside the atlas
                            dist = abs(xi) +  abs(yi)  + abs(zi) # Distance metric
                            # check if the new distance 'dist' is less than the previously seen distance or not
                            if dist <= old_dist: #or final_itr == [0,0,0]
#                                 print(old_dist, dist)
                                old_dist = dist
                                coord_list.append([x-xi, y-yi, z-zi])
                                final_itr = [xi,yi,zi]
#                                 print(final_itr)
                                itr_list.append([xi,yi,zi])
                                roi_list.append(roiNumber)
                                max_prob_list.append(max_prob)

                        vec_of_prob[roiNumber - 1] = 0 # to find second highest region

                    if len(roi_list) != 0:
                        final_roi_list = roi_list
                        final_coord_list = coord_list
                        final_itr_list = itr_list
                        final_max_prob_list = max_prob_list

        return final_roi_list, final_coord_list, final_itr_list, final_max_prob_list



# In[70]:
if __name__ == "__main__":

    # atlasPaths1  = ['hoAtlas/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz',\
    #                'hoAtlas/HarvardOxford-sub-maxprob-thr25-2mm.nii.gz',
    #                'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz']
    # atlasLabelsPaths1 = ['hoAtlas/HarvardOxford-Cortical.xml','hoAtlas/HarvardOxford-Subcortical.xml',\
    #                     'cerebellumAtlas/Cerebellum_MNIflirt.xml']

    atlasPaths1  = ['hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz','hoAtlas/HarvardOxford-cort-maxprob-thr0-1mm.nii.gz',
    'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr0-1mm.nii.gz']

    # atlasPaths1  = ['hoAtlas/HarvardOxford-sub-prob-1mm.nii.gz',\
    # 'hoAtlas/HarvardOxford-cort-prob-1mm.nii.gz',
    # 'cerebellumAtlas/Cerebellum-MNIflirt-prob-1mm.nii.gz']

    atlasLabelsPaths1 = ['hoAtlas/HarvardOxford-Subcortical.xml','hoAtlas/HarvardOxford-Cortical.xml', \
    'cerebellumAtlas/Cerebellum_MNIflirt.xml']




    q1 = queryAtlas(atlasPaths1,atlasLabelsPaths1,False)


    # In[71]:
    # q1.getAtlasRegions([-6,62,-2])
    q1.getAtlasRegions([47,-60, 4])
    # q1.getAtlasRegions([33, -6, -6])

    # In[72]:

    # atlasPath2 = ['juelichAtlas/Juelich-maxprob-thr25-1mm.nii.gz']
    atlasPath2 = ['juelichAtlas/Juelich-maxprob-thr0-1mm.nii.gz']
    # atlasPath2 = ['juelichAtlas/Juelich-prob-1mm.nii.gz']

    atlasLabelsPath2 = ['juelichAtlas/Juelich.xml']
    q2 = queryAtlas(atlasPath2,atlasLabelsPath2,False)

    # In[73]:
    q2.getAtlasRegions([33, -6, -6])
