
# coding: utf-8

# In[65]:


import pandas as pd
import nibabel as nib
import numpy as np
import math
import xml.etree.ElementTree as ET
from tqdm import tqdm
from utils import atlasUtility as au
from utils import brainnetomeUtility as bu



class addAtlasNamestoCSV:
    def __init__(self,BNAtlasObj,HOAtlasObj,JuliechAtlasObj):
        self.BNAtlasObj = BNAtlasObj
        self.HOAtlasObj = HOAtlasObj
        self.JuliechAtlasObj = JuliechAtlasObj

    @staticmethod
    def extract_columns_and_save_CSV(self,csv_path, column_index_include, filename):
        """
        Reads CSV file and saves the selected columns
        Returns pandas data frame
        Can be called as addAtlasNamestoCSV.extract_columns_and_save_CSV() or self.extract_columns_and_save_CSV()
        """
        column_index_include = np.array(column_index_include)
        df = pd.read_csv(csv_path)
        df_extracted = df.iloc[:,column_index_include]
        df_extracted.to_csv(fileName)
        return df_extracted


    def addNameCSV(self, csvPath, filename, column_index_include):
        # read CSV file
        df = pd.read_csv(csvPath)

        column_index_include = np.array(column_index_include)

        dfExtra = df.iloc[:,column_index_include]

        dfMatrix = df.as_matrix(['S_No','PaperID','SeedName', 'SeedMNI', 'UnderConnectivityName', 'UnderConnectivityMNI', 'OverConnectivityName',\
             'OverConnectivityMNI'])


        df_new = pd.DataFrame()

        for ix, row in enumerate(tqdm(dfMatrix)):
            s_no, paperID, seedName, seedMNI, underConnectivityName, underConnectedMNI,overConnectivityName, overConnectedMNI = row

            underConnectivityNameHO = None
            overConnectivityNameHO = None
            hemisphereSeed=None
            hemisphereUC=None
            hemisphereOC=None


            #-------Check if MNI is NAN-----

            if not pd.isna(seedMNI):

                seedMNI = seedMNI.strip('\n')
                seedMNIint = seedMNI.split(' ')
                seedMNIint = [x for x in seedMNIint if x != '']

                try:
                    seedMNIint = list(map(int, seedMNIint))
                except ValueError as v:
                    print(v)
                    print('error at S.No %s'% s_no)


                assert (len(seedMNIint) == 3), "Seed MNI Coordinates Error at S.No %s" % s_no

                if seedMNIint[0] < 0:
                    hemisphereSeed = 'L'
                elif seedMNIint[0] > 0:
                    hemisphereSeed = 'R'
                else:
                    hemisphereSeed = 'C'


                seed_x = seedMNIint[0]
                seed_y = seedMNIint[1]
                seed_z = seedMNIint[2]


                _,seedNameHO,_ = self.HOAtlasObj.getAtlasRegions(seedMNIint)
                _,seedNameJuliech,_ = self.JuliechAtlasObj.getAtlasRegions(seedMNIint)

                _,seedLobe, seedGyrus, seedNameBN = self.BNAtlasObj.getAtlasRegions(seedMNIint)

            else:
                seedNameHO = np.nan
                seedNameJuliech = np.nan
                seedLobe = np.nan
                seedGyrus = np.nan
                seedNameBN = np.nan
                hemisphereSeed = np.nan
                seed_x = np.nan
                seed_y = np.nan
                seed_z = np.nan



            if not pd.isna(underConnectedMNI):
                underConnectedMNI = underConnectedMNI.strip('\n')
                underConnectedMNIint = underConnectedMNI.split(' ')
                underConnectedMNIint = [x for x in underConnectedMNIint if x != '']

                try:
                    underConnectedMNIint = list(map(int, underConnectedMNIint))
                except ValueError as v:
                    print(v)
                    print('error at S.No %s'% s_no)

                assert (len(underConnectedMNIint) == 3), "Underconn. MNI Coordinates Error at S.No %s" % s_no

                if underConnectedMNIint[0] < 0:
                    hemisphereUC = 'L'
                elif underConnectedMNIint[0] > 0:
                    hemisphereUC = 'R'
                else:
                    hemisphereUC = 'C'



                connectivity_x = underConnectedMNIint[0]
                connectivity_y = underConnectedMNIint[1]
                connectivity_z = underConnectedMNIint[2]

                _,connectivityNameHO,_ = self.HOAtlasObj.getAtlasRegions(underConnectedMNIint)
                _,connectivityNameJuliech,_ = self.JuliechAtlasObj.getAtlasRegions(underConnectedMNIint)

                _,connectivityLobe, connectivityGyrus, connectivityNameBN = self.BNAtlasObj.getAtlasRegions(underConnectedMNIint)


                _df = pd.DataFrame({'S_No': [s_no],
                                    'PaperID':[paperID],
                                    'SeedHemisphere':[hemisphereSeed],
                                     'SeedLobe':[seedLobe],
                                     'SeedGyrus':[seedGyrus],
                                     'SeedNameBN':[seedNameBN],
                                     'SeedNameHO':[seedNameHO],
                                     'SeedNameJuliech':[seedNameJuliech],
                                     'SeedName':[seedName],
                                     'Seed_X':[seed_x],
                                     'Seed_Y':[seed_y],
                                     'Seed_Z':[seed_z],
                                     'ConnectivityHemisphere':[hemisphereUC],
                                     'ConnectivityLobe':[connectivityLobe],
                                     'ConnectivityGyrus':[connectivityGyrus],
                                     'ConnectivityNameBN':[connectivityNameBN],
                                     'ConnectivityNameHO':[connectivityNameHO],
                                     'ConnectivityNameJuliech':[connectivityNameJuliech],
                                     'ConnectivityName':[underConnectivityName],
                                     'Connectivity_X':[connectivity_x],
                                     'Connectivity_Y':[connectivity_y],
                                     'connectivity_Z':[connectivity_z],
                                     'Under(-1)/Over(1)Connectivity':[-1],

              })


                dat1 = dfExtra[ix:ix+1]
                dat2 = _df

                dat1 = dat1.reset_index(drop=True)
                dat2 = dat2.reset_index(drop=True)

                temp = pd.concat([dat1,dat2],axis=1)
                df_new = df_new.append(temp)


            if not pd.isna(overConnectedMNI):
                overConnectedMNI = overConnectedMNI.strip('\n')
                overConnectedMNIint = overConnectedMNI.split(' ')
                overConnectedMNIint = [x for x in overConnectedMNIint if x != '']

                try:
                    overConnectedMNIint = list(map(int, overConnectedMNIint))
                except ValueError as v:
                    print(v)
                    print('error at S.No %s'% s_no)

                assert (len(overConnectedMNIint) == 3), "Overconn. MNI Coordinates Error at S.No %s" % s_no

                if overConnectedMNIint[0] < 0:
                    hemisphereOC = 'L'
                elif overConnectedMNIint[0] > 0:
                    hemisphereOC = 'R'
                else:
                    hemisphereOC = 'C'


                connectivity_x = overConnectedMNIint[0]
                connectivity_y = overConnectedMNIint[1]
                connectivity_z = overConnectedMNIint[2]

                _,connectivityNameHO,_ = self.HOAtlasObj.getAtlasRegions(overConnectedMNIint)
                _,connectivityNameJuliech,_ = self.JuliechAtlasObj.getAtlasRegions(overConnectedMNIint)

                _,connectivityLobe, connectivityGyrus, connectivityNameBN = self.BNAtlasObj.getAtlasRegions(overConnectedMNIint)


                _df = pd.DataFrame({'S_No': [s_no],
                                    'PaperID':[paperID],
                                    'SeedHemisphere':[hemisphereSeed],
                                     'SeedLobe':[seedLobe],
                                     'SeedGyrus':[seedGyrus],
                                     'SeedNameBN':[seedNameBN],
                                     'SeedNameHO':[seedNameHO],
                                     'SeedNameJuliech':[seedNameJuliech],
                                     'SeedName':[seedName],
                                     'Seed_X':[seed_x],
                                     'Seed_Y':[seed_y],
                                     'Seed_Z':[seed_z],
                                     'ConnectivityHemisphere':[hemisphereOC],
                                     'ConnectivityLobe':[connectivityLobe],
                                     'ConnectivityGyrus':[connectivityGyrus],
                                     'ConnectivityNameBN':[connectivityNameBN],
                                     'ConnectivityNameHO':[connectivityNameHO],
                                     'ConnectivityNameJuliech':[connectivityNameJuliech],
                                     'ConnectivityName':[overConnectivityName],
                                     'Connectivity_X':[connectivity_x],
                                     'Connectivity_Y':[connectivity_y],
                                     'connectivity_Z':[connectivity_z],
                                     'Under(-1)/Over(1)Connectivity':[1],

              })






                dat1 = dfExtra[ix:ix+1]
                dat2 = _df

                dat1 = dat1.reset_index(drop=True)
                dat2 = dat2.reset_index(drop=True)

                temp = pd.concat([dat1,dat2],axis=1)
                df_new = df_new.append(temp)




        cols=['S_No','PaperID','SeedHemisphere','SeedLobe','SeedGyrus', 'SeedNameBN',\
                                       'SeedNameHO','SeedNameJuliech','SeedName',\
                                       'Seed_X','Seed_Y','Seed_Z', 'ConnectivityHemisphere','ConnectivityLobe',
                                       'ConnectivityGyrus','ConnectivityNameBN',\
                                       'ConnectivityNameHO','ConnectivityNameJuliech','ConnectivityName','Connectivity_X',\
                                       'Connectivity_Y','connectivity_Z', 'Under(-1)/Over(1)Connectivity']



        df_new = df_new.loc[:,dfExtra.columns.append(pd.Index(cols))]
#         fileName = 'connectivityResults2.csv'1

        print('Saving the CSV file of links at %s'% filename)
        df_new.to_csv(filename,index=False)

        return df_new

    @staticmethod
    def remove_duplicate_rows(columns_index, in_file, out_file):
        # TODO:
        # Find the S.No that has duplicate entries
        # Delete that Row

        # read CSV file
        csvPath = in_file
        df = pd.read_csv(csvPath)
        columns_check = list(df.columns[column_index])

        df_extracted = df.drop_duplicates(subset=columns_check,keep='first')

        df_extracted.to_csv(out_file, index=False)
        return df_extracted

    @staticmethod
    def remove_blank_links(columns_index, in_file, out_file, dropped_file):
        """
        Removes the links/rows that contain blanks in the columns specified by columns_index
        out_file contains all the links after dropping the blank links
        dropped_file contains the blank links that were dropped

        The function returns the final fully populated non blank dataframe - df_final
        And the data frame that contains the dropped links - df_dropped
        """
        # read CSV file
        csvPath = in_file
        df = pd.read_csv(csvPath)

        blank_links_list = []
        # Find the row number of blank link
        # df.iloc[:,45].as_matrix()

        for col_idx in column_index:
            blank_links_list.extend(list(np.where(pd.isna(df.iloc[:,col_idx]) == True)[0]))

        blank_links_list = list(set(blank_links_list))

        df_dropped = df.iloc[blank_links_list,:]
        df_final = df.drop(df.index[blank_links_list])
        df_final.to_csv(out_file,index=False)
        df_dropped.to_csv(dropped_file,index=False)
        return df_final, df_dropped

    @staticmethod
    def find_consistent_conflicting_links(df, columns_match_index, connectivity_column_index, s_no_column_index,\
                                          paper_id_column_index,ignore_hemispheres= False):
        conflicts = []
        consistent = []

        df_conflicts_details = pd.DataFrame()
        df_consistent_details = pd.DataFrame()

        if ignore_hemispheres: # need to test it. Looks wrong. Might break node creation
            _columns_match_index = np.array(columns_match_index)[[1,3]]
            print('Hemispheres ignored while checking consistency')
        else:
            _columns_match_index = columns_match_index

        for ix1, (Index, row1) in  tqdm(enumerate(df.iterrows())):
            for ix2, row2 in df[ix1+1:].iterrows():
#                 print(row1[1], row2[1]) # printing S_no pairs
                # if all the columns match/ Same links
                node1 = {tuple(row1[_columns_match_index[0:math.floor(len(_columns_match_index)/2)]]), tuple(row1[_columns_match_index[math.floor(len(_columns_match_index)/2):]])}
                node2 = {tuple(row2[_columns_match_index[0:math.floor(len(_columns_match_index)/2)]]), tuple(row2[_columns_match_index[math.floor(len(_columns_match_index)/2):]])}
#                 print('Node 1 and 2', node1, node2)
                # Created the above nodes to make sure that the link AB and BA are treated equally
                if node1 == node2:
                    if (row1[connectivity_column_index] !=  row2[connectivity_column_index]).sum() == len(connectivity_column_index):
                        # Conflict
                        conflicts.append([(row1[s_no_column_index].item(), row2[s_no_column_index].item()),\
                                          (row1[paper_id_column_index].item(), row2[paper_id_column_index].item())])


                        _df = pd.DataFrame({'S_No_link1': [row1[s_no_column_index].item()],
                                            'PaperID_link1':[row1[paper_id_column_index].item()],
                                            'SeedHemisphere_link1':[row1[columns_match_index[0]]],
                                             'SeedNameHO_link1':[row1[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link1':[row1[columns_match_index[2]]],
                                             'ConnectivityNameHO_link1':[row1[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link1':[row1[connectivity_column_index].item()],

                                            'S_No_link2': [row2[s_no_column_index].item()],
                                            'PaperID_link2':[row2[paper_id_column_index].item()],
                                            'SeedHemisphere_link2':[row2[columns_match_index[0]]],
                                             'SeedNameHO_link2':[row2[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link2':[row2[columns_match_index[2]]],
                                             'ConnectivityNameHO_link2':[row2[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link2':[row2[connectivity_column_index].item()]

                        })

                        df_conflicts_details = df_conflicts_details.append(_df)
                    else:
                        # Consistent
                        consistent.append([(row1[s_no_column_index].item(), row2[s_no_column_index].item()),\
                                          (row1[paper_id_column_index].item(), row2[paper_id_column_index].item())])


                        _df = pd.DataFrame({'S_No_link1': [row1[s_no_column_index].item()],
                                            'PaperID_link1':[row1[paper_id_column_index].item()],
                                            'SeedHemisphere_link1':[row1[columns_match_index[0]]],
                                             'SeedNameHO_link1':[row1[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link1':[row1[columns_match_index[2]]],
                                             'ConnectivityNameHO_link1':[row1[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link1':[row1[connectivity_column_index].item()],

                                            'S_No_link2': [row2[s_no_column_index].item()],
                                            'PaperID_link2':[row2[paper_id_column_index].item()],
                                            'SeedHemisphere_link2':[row2[columns_match_index[0]]],
                                             'SeedNameHO_link2':[row2[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link2':[row2[columns_match_index[2]]],
                                             'ConnectivityNameHO_link2':[row2[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link2':[row2[connectivity_column_index].item()]

                        })

                        df_consistent_details = df_consistent_details.append(_df)

        return df_conflicts_details, df_consistent_details

    @staticmethod
    def order_links_end_points(in_file,links_columns,links_columns_all_details,out_file):
        """
        Code to make all the same links have same end points so that they can be beneficial in the creating pivot table
        links_columns: The columns representing the Hemisphere and Names of the regions of both the link end points
        links_columns_all_details: The columns representing all the other details associated with the node such as
        MNI coordinates, names according to other atlases etc.

        Returns the ordered dataframe and saves the csv file

        Usage: className.order_links_end_points(in_file,links_columns,links_columns_all_details,out_file)
        links_columns_all_details: Divides this vector into 2 - source and destination details and then swaps them
        """

        df = pd.read_csv(in_file)#.iloc[:,1:]
    #     links_columns =  [41,45,51,55]
        links_node_swapped_columns = links_columns[math.floor(len(links_columns)/2):] + links_columns[0:math.floor(len(links_columns)/2)]


    #     links_columns_all_details =  list(np.arange(41,61))
        links_node_swapped_columns_all_details = links_columns_all_details[math.floor(len(links_columns_all_details)/2):] + links_columns_all_details[0:math.floor(len(links_columns_all_details)/2)]


        for ix1, (Index, row1) in  tqdm(enumerate(df.iterrows())):
            for ix2, (Index, row2) in enumerate(df[ix1+1:].iterrows()):


                if (row1[links_columns].as_matrix() == row2[links_node_swapped_columns].as_matrix()).all():
    #                 print('swapping',ix1,ix1 + 1 +ix2)
        #             import ipdb; ipdb.set_trace()
        #             print('Row2',row2)
                    temp = []
                    for i in range(len(links_columns_all_details)):

                        if i < math.floor(len(links_columns_all_details)/2):
                            temp.append(df.iat[ix1 + 1 + ix2, links_columns_all_details[i]])
                            df.iat[ix1 + 1 + ix2, links_columns_all_details[i]] = df.iat[ix1 + 1 + ix2, links_node_swapped_columns_all_details[i]]
                        else:
                            df.iat[ix1 + 1 + ix2, links_columns_all_details[i]] = temp[i - math.floor(len(links_columns_all_details)/2)]

    #                 print('swapped',ix1,ix1 + 1 +ix2)
        #             print('Row1', row1,'Row2', row2)
        #             import ipdb; ipdb.set_trace()



        df.to_csv(out_file, index=False)

        return df

    #TODO
    @staticmethod
    def find_consistent_conflicting_links_score(df_ordered, columns_match_index, connectivity_column_index, s_no_column_index,\
                                          paper_id_column_index,ignore_hemispheres= False):
        conflicts = []
        consistent = []

        df = df_ordered
        df_conflicts_details = pd.DataFrame()
        df_consistent_details = pd.DataFrame()

        if ignore_hemispheres: # need to test it. Looks wrong. Might break node creation
            _columns_match_index = np.array(columns_match_index)[[1,3]]
            print('Hemispheres ignored while checking consistency')
        else:
            _columns_match_index = columns_match_index

        for ix1, (Index, row1) in  tqdm(enumerate(df.iterrows())):
            for ix2, row2 in df[ix1+1:].iterrows():
#                 print(row1[1], row2[1]) # printing S_no pairs
                # if all the columns match/ Same links
                node1 = {tuple(row1[_columns_match_index[0:math.floor(len(_columns_match_index)/2)]]), tuple(row1[_columns_match_index[math.floor(len(_columns_match_index)/2):]])}
                node2 = {tuple(row2[_columns_match_index[0:math.floor(len(_columns_match_index)/2)]]), tuple(row2[_columns_match_index[math.floor(len(_columns_match_index)/2):]])}
#                 print('Node 1 and 2', node1, node2)
                # Created the above nodes to make sure that the link AB and BA are treated equally
                if node1 == node2:
                    if (row1[connectivity_column_index] !=  row2[connectivity_column_index]).sum() == len(connectivity_column_index):
                        # Conflict
                        conflicts.append([(row1[s_no_column_index].item(), row2[s_no_column_index].item()),\
                                          (row1[paper_id_column_index].item(), row2[paper_id_column_index].item())])


                        _df = pd.DataFrame({'S_No_link1': [row1[s_no_column_index].item()],
                                            'PaperID_link1':[row1[paper_id_column_index].item()],
                                            'SeedHemisphere_link1':[row1[columns_match_index[0]]],
                                             'SeedNameHO_link1':[row1[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link1':[row1[columns_match_index[2]]],
                                             'ConnectivityNameHO_link1':[row1[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link1':[row1[connectivity_column_index].item()],

                                            'S_No_link2': [row2[s_no_column_index].item()],
                                            'PaperID_link2':[row2[paper_id_column_index].item()],
                                            'SeedHemisphere_link2':[row2[columns_match_index[0]]],
                                             'SeedNameHO_link2':[row2[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link2':[row2[columns_match_index[2]]],
                                             'ConnectivityNameHO_link2':[row2[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link2':[row2[connectivity_column_index].item()]

                        })

                        df_conflicts_details = df_conflicts_details.append(_df)
                    else:
                        # Consistent
                        consistent.append([(row1[s_no_column_index].item(), row2[s_no_column_index].item()),\
                                          (row1[paper_id_column_index].item(), row2[paper_id_column_index].item())])


                        _df = pd.DataFrame({'S_No_link1': [row1[s_no_column_index].item()],
                                            'PaperID_link1':[row1[paper_id_column_index].item()],
                                            'SeedHemisphere_link1':[row1[columns_match_index[0]]],
                                             'SeedNameHO_link1':[row1[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link1':[row1[columns_match_index[2]]],
                                             'ConnectivityNameHO_link1':[row1[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link1':[row1[connectivity_column_index].item()],

                                            'S_No_link2': [row2[s_no_column_index].item()],
                                            'PaperID_link2':[row2[paper_id_column_index].item()],
                                            'SeedHemisphere_link2':[row2[columns_match_index[0]]],
                                             'SeedNameHO_link2':[row2[columns_match_index[1]]],
                                             'ConnectivityHemisphere_link2':[row2[columns_match_index[2]]],
                                             'ConnectivityNameHO_link2':[row2[columns_match_index[3]]],
                                             'Under(-1)/Over(1)Connectivity_link2':[row2[connectivity_column_index].item()]

                        })

                        df_consistent_details = df_consistent_details.append(_df)

        return df_conflicts_details, df_consistent_details

def show_columns(df):
    """
    This function gives a quick viwe of what are the columns and their corresponding indices
    of a csv file or dataframe.

    Input: CSV file path or a pandas Dataframe
    Output: Displays the columns along with their index

    """

    if isinstance(df,str):
        df = pd.read_csv(df)

    ind = np.arange(len(df.columns))

    for entry in zip(ind,df.columns):
        print(entry)


if __name__ == "__main__":

    REMOVE_DUPLICATES =  False
    CONSISTENT_INCONSISTENT_LINKS = False
    # atlas_path = 'brainnetomeAtlas/BNA-maxprob-thr0-1mm.nii.gz'
    atlas_path = 'brainnetomeAtlas/BNA-prob-2mm.nii.gz'
    atlasRegionsDescrpPath = 'brainnetomeAtlas/BNA_subregions_machineReadable.xlsx'

    BNAtlasObj = bu.queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath,True)


    # atlasPaths1  = ['hoAtlas/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz',\
    #                'hoAtlas/HarvardOxford-sub-maxprob-thr25-2mm.nii.gz',
    #                'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz']
    # atlasLabelsPaths1 = ['hoAtlas/HarvardOxford-Cortical.xml','hoAtlas/HarvardOxford-Subcortical.xml',\
    #                     'cerebellumAtlas/Cerebellum_MNIflirt.xml']

    # atlasPaths1  = ['hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz',\
    #                'hoAtlas/HarvardOxford-cort-maxprob-thr0-1mm.nii.gz',
    #                'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr0-1mm.nii.gz']

    atlasPaths1  = ['hoAtlas/HarvardOxford-sub-prob-1mm.nii.gz',\
                   'hoAtlas/HarvardOxford-cort-prob-1mm.nii.gz',
                   'cerebellumAtlas/Cerebellum-MNIflirt-prob-1mm.nii.gz']

    atlasLabelsPaths1 = ['hoAtlas/HarvardOxford-Subcortical.xml','hoAtlas/HarvardOxford-Cortical.xml',\
                        'cerebellumAtlas/Cerebellum_MNIflirt.xml']


    HOAtlasObj = au.queryAtlas(atlasPaths1,atlasLabelsPaths1,True)


    # atlasPath2 = ['juelichAtlas/Juelich-maxprob-thr25-1mm.nii.gz']
    # atlasPath2 = ['juelichAtlas/Juelich-prob-1mm.nii.gz']
    # atlasLabelsPath2 = ['juelichAtlas/Juelich.xml']
    #
    # JuliechAtlasObj = au.queryAtlas(atlasPath2,atlasLabelsPath2,True)


    atlasPath3 = ['Schaefer_4d_Atlas_7_Networks.nii.gz']
    atlasLabelsPath3 = ['schaeferAtlas/Schaefer_4d_Atlas_7_Networks_1mm.xml']
    SchaeferAtlasObj = au.queryAtlas(atlasPath3, atlasLabelsPath3, True)


    csvPath = 'csv_input/als.csv'
    # q = addAtlasNamestoCSV(BNAtlasObj, HOAtlasObj, JuliechAtlasObj)

    q = addAtlasNamestoCSV(BNAtlasObj, HOAtlasObj, SchaeferAtlasObj)


    # columns_index_include = [0,1,28,29,30,31]

    # columns_index_include = [0,1]
    # columns_index_include.extend(list(np.arange(3,41)))

    columns_index_include = list(np.arange(3,41))

    filename = 'csv_output/finalLinks_all_columns.csv'
    df = q.addNameCSV(csvPath, filename, columns_index_include)
    # df = q.addNameCSV(csvPath, filename)

    # import pdb;pdb.set_trace()
    # Remov the blank links

    in_file = 'csv_output/finalLinks_all_columns.csv'
    out_file = 'csv_output/finalLinks_blanks_dropped_all_columns.csv'
    dropped_file = 'csv_output/dropped_all_columns.csv'


    # column_index = [45,55]
    column_index = [44,54]
    df_final, df_dropped = addAtlasNamestoCSV.remove_blank_links(column_index,in_file,out_file,dropped_file)

    # Remove Duplicates

    # Remove Duplicates: For each paper ID independently, remove the link that has same hemisphere HO region
    # as source and target and that has same connectivity value

    # import pdb;pdb.set_trace()

    if REMOVE_DUPLICATES:
        in_file = 'csv_output/finalLinks_blanks_dropped_all_columns.csv'
        out_file = 'csv_output/finalLinks_duplicates_removed_all_columns.csv'
        # column_index = [4,13,17,23,27,33]

        # column_index = [40,41,45,51,55,61]
        column_index = [39,40,44,50,54,60]

        df_extracted = addAtlasNamestoCSV.remove_duplicate_rows(column_index,in_file,out_file)
        in_file = 'csv_output/finalLinks_duplicates_removed_all_columns.csv' # For next Step
    else:
        in_file = 'csv_output/finalLinks_blanks_dropped_all_columns.csv'




    # Order the link nodes

    # Code to make all the same links have same end points so that they can be beneficial in the creating pivot table
    # in_file = 'csv_output/finalLinks_duplicates_removed_all_columns.csv'
    out_file = 'csv_output/finalLinks_duplicates_removed_ordered_all_columns_incl_networks.csv'
    # links_columns =  [41,45,51,55]
    links_columns =  [40,44,50,54]

    links_columns_all_details =  list(np.arange(40,60))
    df_ordered = addAtlasNamestoCSV.order_links_end_points(in_file,links_columns,links_columns_all_details,out_file)

    # import pdb;pdb.set_trace()

    # Consistent and conflicting links

    # Match the rows having same hemisphere and same HO region


    # columns_match_index = [13, 17, 23, 27]

    # connectivity_column_index = [33]
    # s_no_column_index = [1]
    # paper_id_column_index = [3]

    # columns match index of the form []
    # columns_match_index = [41,45,51,55]
    columns_match_index = [40,44,50,54]

    # columns_match_index = [45,55]

    # connectivity_column_index = [61]
    # s_no_column_index = [39]
    # paper_id_column_index = [40]

    connectivity_column_index = [60]
    s_no_column_index = [38]
    paper_id_column_index = [39]


    if CONSISTENT_INCONSISTENT_LINKS:
        # TODO exchange df_extracted by file name
        df_conflicts_details, df_consistent_details = addAtlasNamestoCSV.find_consistent_conflicting_links(df_extracted, columns_match_index, connectivity_column_index,\
        s_no_column_index, paper_id_column_index, ignore_hemispheres = False)

    # import pdb;pdb.set_trace()
