
# coding: utf-8

# In[65]:


import pandas as pd
import nibabel as nib
import numpy as np
import math
import xml.etree.ElementTree as ET
from tqdm import tqdm


# In[66]:


class queryBrainnetomeROI:
    """
    Class queryBrainnetomeROI provides methods by which you can accomplish the following:
    - Given ROI number get [Lobe, Gyrus, Region and MNI Coordinates] using queryDict(ROI_number) or queryDict([ROI_numbers])
    - Given MNI coordinates get [Lobe, Gyrus, Region and MNI Coordinates] using getAtlasRegions([x,y,z])
    Usage:
    >>> atlas_path = 'BNA-maxprob-thr0-1mm.nii.gz' # path to the atlas file
    >>> atlasRegionsDescrpPath = 'brainnetomeAtlas/BNA_subregions_machineReadable.xlsx' # path to ROI description xlsx
    >>> q = queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath)
    >>> q.queryDict(246)
    [array(['Subcortical Nuclei', 'Tha, Thalamus',
        'Tha_lPFtha, lateral pre-frontal thalamus', '13, -16, 7 '],
       dtype=object)]

    Also, this function supports the use of 4D probability map of the atlas to find the nearby
    maximim probability region in the vicinity of 3 voxel cube if the region at a particular voxel is not
    present in the atlas.
    Set prob = True  and provide a 4D nii.gz file path as atlas_path
    """
    def __init__(self, atlas_path, atlasRegionsDescrpPath , prob = False ):
        self.atlas_path = atlas_path

        self.prob = prob


        _atlas = nib.load(self.atlas_path)
        self.atlas = _atlas.get_data()

        print('Atlas read')
        if _atlas.header['pixdim'][1] == 2:
            self.pixdim = 2
#             x,y,z = self.MNI2XYZ2mm(coordMni)
        elif _atlas.header['pixdim'][1] == 1:
            self.pixdim = 1
#             x,y,z = self.MNI2XYZ1mm(coordMni)
        else:
            raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )

        print('checked Pixel dimension')

        self.numSeeds = None
        self.atlasRegionsDescrpPath = atlasRegionsDescrpPath


    def MNI2XYZ1mm(self, mni):
        x =  - mni[0] + 90
        y = mni[1] + 126
        z = mni[2] + 72
        return [x,y,z]

    def MNI2XYZ2mm(self, mni):
        x =  math.floor((- mni[0] + 90)/2.0)
        y = math.floor((mni[1] + 126)/2.0)
        z = math.floor((mni[2] + 72)/2.0)
        return [x,y,z]

    def brainnetomeQuery(self):
        """
        Extract the region names from excel file and creates a dictionary i.e. key value pair
        where Key is the ROI number and Value is the list of [Lobe, Gyrus, Region and MNI Coordinates]
        of the query ROI Number.

        """
#         atlas = nib.load(self.atlas_path).get_data()
        df = pd.read_excel(self.atlasRegionsDescrpPath)

        if self.prob:
            self.numSeeds = self.atlas.shape[3]
        else:
            self.numSeeds = int(np.max(self.atlas))

        df = df.as_matrix(['Lobe','Gyrus','Label ID.L', 'Label ID.R','Left and Right Hemisphere','Unnamed: 5', 'lh.MNI(X,Y,Z)', 'rh.MNI(X,Y,Z)'])
        seedInfo = np.empty((self.numSeeds + 1, 5),dtype=object)

        for lobe, gyrus, i,j,region,label,lcoord,rcoord in df:
            seedInfo[i,:] = i,lobe, gyrus, region.split('_')[0] + '_' + label, lcoord
            seedInfo[j,:] = j,lobe, gyrus, region.split('_')[0] + '_' + label, rcoord


        # Create a dictionary of seedInfo so that it can be accessed by roi number

        ROI_dictionary = {}
        for i in seedInfo[1:]:
            ROI_dictionary[i[0]] = i[1:]

        return ROI_dictionary



    def queryDict(self, lis): # lis: List that contains ROI numbers (1 to 246)
        """
        Used yhe dicrionary created by self.brainnetomeQuery() and ...
        Returns the list of [Lobe, Gyrus, Region and MNI Coordinates] of the query ROI Number
        """

        ROI_dictionary = self.brainnetomeQuery()
        return_regions = []

        # If input is a list of ROI numbers
        if isinstance(lis,list):
            for i in lis:
                try: return_regions.append(ROI_dictionary[i])
                except KeyError:
                    # returns List of None if ROI number is not found. ROI = [1,246]
                    return_regions.append([None,None,None,None])

        # If input is just a single ROI number
        else:
            i = lis
            try: return_regions.append(ROI_dictionary[i])
            except KeyError:
                return_regions.append([None,None,None,None])


        return return_regions

    def getAtlasRegions(self, coordMni):
        """
        Converts the MNI coordinates to image coordinates by using MNI2XYZ2mm() or MNI2XYZ1mm()
        It calls self.queryDict() in the background
        Returns the list of [Lobe, Gyrus, Region and MNI Coordinates] of the query MNI Coordinate.
        """
#         _atlas = nib.load(self.atlas_path)
#         atlas = _atlas.get_data()
#         if _atlas.header['pixdim'][1] == 2:
        if self.pixdim == 2:
            x,y,z = self.MNI2XYZ2mm(coordMni)
#         elif _atlas.header['pixdim'][1] == 1:
        elif self.pixdim == 1:
            x,y,z = self.MNI2XYZ1mm(coordMni)
#         else:
#             raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )
        if self.prob == False:
            roiNumber = self.atlas[x,y,z]
        else:
            vec_of_prob = self.atlas[x,y,z,:]
            roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
            max_prob =  vec_of_prob[roiNumber-1]
            if max_prob == 0: # # Coordinate is outside the atlas
                itr = [0,1,-1,2,-2,3,-3]
                roiNumber, final_coord, final_itr = self.get_neighbouring_coordinates(x,y,z,itr)



        lobe, gyrus, roiName, _ = self.queryDict(roiNumber)[0]
        return int(roiNumber),lobe, gyrus, roiName

    def get_neighbouring_coordinates(self,x,y,z,itr):
        final_coord = [x,y,z]
        old_dist = float('Inf')
        final_itr = [0,0,0]
        final_roi = 0
        for xi in itr:
            for yi in itr:
                for zi in itr:
                    vec_of_prob = self.atlas[x-xi,y-yi,z-zi,:]
                    roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
                    max_prob =  vec_of_prob[roiNumber - 1]
#                     print('coord',x-xi,y-yi,z-zi)
#                     print('MAx_prob',max_prob)
                    if max_prob != 0: # the max roi lies inside the atlas
                        dist = abs(xi) +  abs(yi)  + abs(zi)
                        if dist < old_dist or final_itr == [0,0,0]:
#                             print('old_dist',old_dist)
                            old_dist = dist
                            final_coord = [x-xi, y-yi, z-zi]
                            final_itr = [xi,yi,zi]
                            final_roi = roiNumber

        return final_roi, final_coord, final_itr






# In[67]:
if __name__ == "__main__":
    atlas_path = 'brainnetomeAtlas/BNA-maxprob-thr0-1mm.nii.gz'
    # atlasRegionsDescrpPath = '/home/varun/Projects/fmri/Autism-Connectome-Analysis-brain_connectivity/atlas/BNA_subregions.xlsx'
    atlasRegionsDescrpPath = 'brainnetomeAtlas/BNA_subregions_machineReadable.xlsx'
    q = queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath, False)


    # In[68]:
    q.queryDict(246) # Returns Lobe, Gyrus, Region and MNI Coordinates of the query ROI Number
