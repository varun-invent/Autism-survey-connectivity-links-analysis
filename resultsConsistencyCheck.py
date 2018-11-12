# coding: utf-8

import numpy as np
import nibabel as nib
import pandas as pd
from tqdm import tqdm
import pandas as pd
import subprocess
import math



class queryBrainnetomeROI:
    def __init__(self, atlas_path, atlasRegionsDescrpPath):
        self.atlas_path = atlas_path
        self.numSeeds = None
        self.atlasRegionsDescrpPath = atlasRegionsDescrpPath
#         self.ROI_dictionary = None


    def brainnetomeQuery(self):

        atlas = nib.load(self.atlas_path).get_data()
        df = pd.read_excel(self.atlasRegionsDescrpPath)

        self.numSeeds = int(np.max(atlas))

        df = df.as_matrix(['Label ID.L', 'Label ID.R','Left and Right Hemisphere','Unnamed: 5', 'lh.MNI(X,Y,Z)', 'rh.MNI(X,Y,Z)'])

        seedInfo = np.empty((self.numSeeds + 1, 3),dtype=object)

        for i,j,region,label,lcoord,rcoord in df:
            seedInfo[i,:] = i, region.split('_')[0] + '_' + label, lcoord
            seedInfo[j,:] = j, region.split('_')[0] + '_' + label, rcoord

    #     seedInfo[1:]

        # Create a dictionary of seedInfo so that it can be accessed by roi number

        ROI_dictionary = {}
        for i in seedInfo[1:]:
            ROI_dictionary[i[0]] = i[1:]

        return ROI_dictionary


    #     d[1]

    def queryDict(self, lis): # lis: List that contains ROI numbers (1 to 246)

        ROI_dictionary = self.brainnetomeQuery()
        return_regions = []


        if isinstance(lis,list):
            for i in lis:
        #         return_regions.append(str(i)+"_"+d[i][0])
                return_regions.append(ROI_dictionary[i][0])
        else:
            i = lis
            return_regions.append(ROI_dictionary[i][0])

        return return_regions




# In[50]:
# atlas_path = 'BNA-maxprob-thr0-1mm.nii.gz'
# atlasRegionsDescrpPath = '/home/varun/Projects/fmri/Autism-Connectome-Analysis-brain_connectivity/atlas/BNA_subregions.xlsx'
# q = queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath)


class queryAtlasROI:
    '''
    Common base class for all the functions to query the atlas
    '''
    def __init__(self, atlas_path):
        self.atlas_path = atlas_path

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

    def HO_region(self, out):
        out_new = []
        i = 0
        for entry in out:
            if 'No label found' in entry:
                return ''
            if (i == 0) and ('Cerebral' in entry):
                return ''
            if '%' in entry:
                out_new.append(entry)
                i=i+1
            else:
                out_new[i-1] = out_new[i-1] + '_'+ entry

        return out_new[0]

    def getHOAtlasRegions(self, coord):

        p1 = subprocess.Popen(["atlasquery", "-a", "Harvard-Oxford Cortical Structural Atlas", "-c", coord ], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["atlasquery", "-a", "Harvard-Oxford Subcortical Structural Atlas", "-c", coord], stdout=subprocess.PIPE)

        out1 = p1.communicate()
        out2 = p2.communicate()

        out = []


        out1 = str(out1[0]).split('<br>')[1].split(',')
        out2 = str(out2[0]).split('<br>')[1].split(',')

        if int(coord.split(',')[0]) < 0:
            hemisphere = '_L'
        else:
            hemisphere = '_R'
        return [self.HO_region(out1) + hemisphere ,  self.HO_region(out2)+ hemisphere ]

    def queryDict_HO(self, coord,roi_number=None):

#         assert isinstance(lis,list)



        return_cortical_regions = []
        return_subcortical_regions = []
#         for i in lis:
        x,y,z = coord
        coord = str(x) +','+ str(y)+ ','+ str(z)
#         print(getHOAtlasRegions(d[i][1]))
        cortical,subcortical = self.getHOAtlasRegions(coord)

        if (cortical == '_L') or (cortical == '_R'):
            cortical = ''
        else:
            if roi_number != None:
                cortical = str(roi_number)+ "_" + cortical


        if (subcortical == '_L') or (subcortical == '_R'):
            subcortical = ''
        else:
            if roi_number != None:
                subcortical = str(roi_number)+ "_" + subcortical

        return_cortical_regions.append(cortical)
        return_subcortical_regions.append(subcortical)
        return return_cortical_regions+return_subcortical_regions

    def getROI(self, seedMNI, mm=1, extraAtlasObject = None, atlas_path = None):

        atlas = nib.load(self.atlas_path).get_data()

        if mm == 1:
            x,y,z = self.MNI2XYZ1mm(seedMNI)
        else:
            x,y,z = self.MNI2XYZ2mm(seedMNI)
        
        roi_number = atlas[x,y,z] # (1 to 246)

        # Now send this ROI number to queryDict function to query about the Brainnetome region

        roiNameHO = self.queryDict_HO(seedMNI,roi_number)

        if extraAtlasObject == None:
            return roi_number, roiNameHO
        else:
            roiNameBrainnetome = extraAtlasObject.queryDict(roi_number)
            return roi_number, roiNameBrainnetome, roiNameHO







class checkConnectivity:
    '''
    queryAtlasObj gives the method to get the ROI number
    queryExtraAtlasObj gives the method to access Brainnetome atlas related methods
    '''
    def __init__(self,brainLogqFile, queryAtlasObj, queryExtraAtlasObj):
        self.brainLogqFile = brainLogqFile
        self.ROIbrain = nib.load(self.brainLogqFile).get_data()
        self.queryAtlasObj=queryAtlasObj
        self.queryExtraAtlasObj=queryExtraAtlasObj

    def MNI2XYZ2mm(self, mni):

        x =  math.floor((- mni[0] + 90)/2.0)
        y = math.floor((mni[1] + 126)/2.0)
        z = math.floor((mni[2] + 72)/2.0)
        return [x,y,z]


    def connectivityCheck(self,seedMNI, voxelMNI, alpha):
        x,y,z = self.MNI2XYZ2mm(voxelMNI)
        roi = int(self.queryAtlasObj.getROI(seedMNI, self.queryExtraAtlasObj )[0])
        print('ROI: ',roi)


        value = self.ROIbrain[x,y,z,roi-1]

        print('Value at given MNI is :',value)
        if value < 0:
            if abs(value) >= alpha:
                code,connectivity = 1, 'Underconnected'
            else:
                code,connectivity = 0, 'n.s'
        if value >= 0:
            if abs(value) >= alpha:
                code, connectivity = 2, 'Overconnected'
            else:
                code, connectivity =  0, 'n.s'

        return code, connectivity

    def connectivityCheckCSV(self,csvPath,alpha):
            # read CSV file
        df = pd.read_csv(csvPath)
        dfMatrix = df.as_matrix(['SeedName', 'SeedMNI', 'UnderConnectivityName', 'UnderConnectivityMNI', 'OverConnectivityName',             'OverConnectivityMNI'])

        df_new = pd.DataFrame(columns=['SeedName', 'SeedMNI', 'UnderConnectivityName', 'UnderConnectivityMNI','ConsistencyUC', 'OverConnectivityName',             'OverConnectivityMNI', 'ConsistencyOC'])
        for row in tqdm(dfMatrix):
            seedName, seedMNI, UnderConnectivityName, UnderConnectedMNI,OverConnectivityName, OverConnectedMNI = row
            print(seedName, seedMNI, UnderConnectivityName, UnderConnectedMNI,OverConnectivityName, OverConnectedMNI)

            seedMNI = seedMNI.strip('\n')


            seedMNIint = seedMNI.split(' ')
            seedMNIint = [x for x in seedMNIint if x != '']

            print('Seed: ',seedMNIint)

            seedMNIint = list(map(int, seedMNIint))

            if not pd.isna(UnderConnectedMNI):
                UnderConnectedMNI = UnderConnectedMNI.strip('\n')
                UnderConnectedMNIint = UnderConnectedMNI.split(' ')
                UnderConnectedMNIint = [x for x in UnderConnectedMNIint if x != '']
                print(UnderConnectedMNIint)
                UnderConnectedMNIint = list(map(int, UnderConnectedMNIint))

                ConsistencyUC = self.connectivityCheck(seedMNIint, UnderConnectedMNIint, alpha)[0]

            else:
                ConsistencyUC = UnderConnectedMNI

            if not pd.isna(OverConnectedMNI):
                OverConnectedMNI = OverConnectedMNI.strip('\n')
                OverConnectedMNIint = OverConnectedMNI.split(' ')
                OverConnectedMNIint = [x for x in OverConnectedMNIint if x != '']
                print(OverConnectedMNIint)
                OverConnectedMNIint = list(map(int, OverConnectedMNIint))

                ConsistencyOC = self.connectivityCheck(seedMNIint, OverConnectedMNIint, alpha)[0]

            else:
                ConsistencyOC = OverConnectedMNI




            df_new = df_new.append({'SeedName':seedName,
                                    'SeedMNI':seedMNI,
                                    'UnderConnectivityName':UnderConnectivityName,
                                    'UnderConnectivityMNI':UnderConnectedMNI,
                                    'ConsistencyUC':ConsistencyUC,
                                    'OverConnectivityName':OverConnectivityName,
                                    'OverConnectivityMNI':OverConnectedMNI,
                                    'ConsistencyOC':ConsistencyOC
              }, ignore_index=True)

        # Extract the seedMNI and UnderConnectedMNI column
        # Call self.connectivityCheck to get the code and connectivity string
        # Create another CSV file with rows -
        # | SeedName, SeedMNI, UnderConnectedName, UnderConnectedMNI, ConsistentCheck,
        #  OverConnectedName, OverConnectedMNI, ConsistentCheck  |

        fileName = 'connectivityResults.csv'
        df_new.to_csv(fileName)

        return df_new, fileName


# In[13]:

if __name__ == "__main__":
    print('Executing the the base file')
    atlas_path = 'BNA-maxprob-thr0-1mm.nii.gz'
    atlasRegionsDescrpPath = '/home/varun/Projects/fmri/Autism-Connectome-Analysis-brain_connectivity/atlas/BNA_subregions.xlsx'


    brainLogqFile = 'map_logq_2mm.nii.gz'
    queryAtlasObj = queryAtlasROI(atlas_path)
    queryExtraAtlasObj =  queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath)
    q3 = checkConnectivity(brainLogqFile, queryAtlasObj, queryExtraAtlasObj)


    alpha = 1.3
    csvPath = 'Literature_Survey_ResultsSheet3.csv'
    q3.connectivityCheckCSV(csvPath,alpha)
