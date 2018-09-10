
# coding: utf-8


import pandas as pd
import nibabel as nib
import numpy as np
import math
import xml.etree.ElementTree as ET
from tqdm import tqdm
from utils import atlasUtility as au
from utils import brainnetomeUtility as bu
import collections as co



class addAtlasNamestoCSV:
    def __init__(self, BNA_atlas_dict, atlas_dict_list = None):
        self.BNAtlasObj = BNA_atlas_dict['obj']
        # self.BNAtlasObj = BNA_atlas_dict['name']

        # self.BNAtlasObj = BNAtlasObj
        if atlas_dict_list:
            self.atlas_dict_list = atlas_dict_list
        # self.HOAtlasObj = HOAtlasObj
        # self.JuliechAtlasObj = JuliechAtlasObj

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


    @staticmethod
    def get_hemisphere(coordinates):
        """
        Input: List of MNI coordinates
        Output: 'L', 'R', 'C'
        """
        if coordinates[0] < 0:
            return 'L'
        elif coordinates[0] > 0:
            return 'R'
        else:
            return 'C'

    def addNameCSV(self, csvPath, filename, column_index_include, read_hemis_from_csv = False):
        # read CSV file
        df = pd.read_csv(csvPath)

        column_index_include = np.array(column_index_include)

        dfExtra = df.iloc[:,column_index_include]

        essential_columns = [
        'S_No','PaperID','SeedName', 'SeedMNI', 'UnderConnectivityName',
        'UnderConnectivityMNI', 'OverConnectivityName', 'OverConnectivityMNI'
        ]

        if read_hemis_from_csv:
            essential_columns.extend(['SeedHem', 'UnderHem', 'OverHem'])


        dfMatrix = df.as_matrix(essential_columns)


        df_new = pd.DataFrame()

        # 'if' condition to read the Hemispheres from the csv
        for ix, row in enumerate(tqdm(dfMatrix)):
            if read_hemis_from_csv:
                s_no, paperID, seedName, seedMNI, underConnectivityName,\
                underConnectedMNI, overConnectivityName, overConnectedMNI,\
                SeedHem, UnderHem, OverHem = row
                # Some preprocessing before using hemisphere information
                SeedHem = SeedHem.strip()
                UnderHem = UnderHem.strip()
                OverHem = OverHem.strip()

            else:
                s_no, paperID, seedName, seedMNI, underConnectivityName,\
                underConnectedMNI,overConnectivityName, overConnectedMNI = row




            # underConnectivityNameHO = None
            # overConnectivityNameHO = None

            # Hemispheric information of the seed and target
            hemisphereSeed = None
            hemisphereUC = None
            hemisphereOC = None



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

                if read_hemis_from_csv:
                    if SeedHem.upper() in ['L','R','C']:
                        hemisphereSeed = SeedHem.upper()
                    elif SeedHem == '-':
                        hemisphereSeed = self.get_hemisphere(seedMNIint)
                    else:
                        raise Exception('Incorrect Hemisphere entry at Seed MNI: ',seedMNI)
                else:
                    hemisphereSeed = self.get_hemisphere(seedMNIint)


                seed_x = seedMNIint[0]
                seed_y = seedMNIint[1]
                seed_z = seedMNIint[2]


                # Brainnetome
                _,seedLobe, seedGyrus, seedNameBN = self.BNAtlasObj.getAtlasRegions(seedMNIint)

                # Loop over atlases (For Seed)
                if self.atlas_dict_list:
                    seedName_list = []
                    for atlas_dict in self.atlas_dict_list:
                        obj = atlas_dict['obj']
                        _, seedname, _ = obj.getAtlasRegions(seedMNIint)
                        seedName_list.append(seedname)


                # _,seedNameHO,_ = self.HOAtlasObj.getAtlasRegions(seedMNIint)
                # _,seedNameJuliech,_ = self.JuliechAtlasObj.getAtlasRegions(seedMNIint)


            else:
                # Brainnetome atlas
                seedLobe = np.nan
                seedGyrus = np.nan
                seedNameBN = np.nan

                # Loop over atlases (For Seed)
                if self.atlas_dict_list:
                    seedName_list = []
                    for atlas_dict in self.atlas_dict_list:
                        seedName_list.append(np.nan)


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


                if read_hemis_from_csv:
                    if UnderHem.upper() in ['L','R','C']:
                        hemisphereUC = UnderHem.upper()
                    elif UnderHem == '-':
                        hemisphereUC = self.get_hemisphere(underConnectedMNIint)
                    else:
                        raise Exception('Incorrect Hemisphere entry at UC MNI: ',underConnectedMNIint)
                else:
                    hemisphereUC = self.get_hemisphere(underConnectedMNIint)


                connectivity_x = underConnectedMNIint[0]
                connectivity_y = underConnectedMNIint[1]
                connectivity_z = underConnectedMNIint[2]

                # Loop over atlases (For target)
                if self.atlas_dict_list:
                    connectivityName_list = []
                    for atlas_dict in self.atlas_dict_list:
                        obj = atlas_dict['obj']
                        _, connectivityname, _ = obj.getAtlasRegions(underConnectedMNIint)
                        connectivityName_list.append(connectivityname)

                # _,connectivityNameHO,_ = self.HOAtlasObj.getAtlasRegions(underConnectedMNIint)
                # _,connectivityNameJuliech,_ = self.JuliechAtlasObj.getAtlasRegions(underConnectedMNIint)

                _,connectivityLobe, connectivityGyrus, connectivityNameBN = self.BNAtlasObj.getAtlasRegions(underConnectedMNIint)

                # Construct the dictionary in the loop and then make it a dataframe

                dataframe_dict = co.OrderedDict({
                                 'S_No': [s_no],
                                 'PaperID':[paperID],
                                 'SeedHemisphere':[hemisphereSeed],
                                 'SeedLobe':[seedLobe],
                                 'SeedGyrus':[seedGyrus],
                                 'SeedNameBN':[seedNameBN]})

                # Add more atlas names (Seed)
                if self.atlas_dict_list:
                    for idx, atlas_dict in enumerate(self.atlas_dict_list):
                        name = atlas_dict['name']
                        dataframe_dict['SeedName'+name] = [seedName_list[idx]]


                _dataframe_dict = co.OrderedDict({
                                 'SeedName':[seedName],
                                 'Seed_X':[seed_x],
                                 'Seed_Y':[seed_y],
                                 'Seed_Z':[seed_z],
                                 'ConnectivityHemisphere':[hemisphereUC],
                                 'ConnectivityLobe':[connectivityLobe],
                                 'ConnectivityGyrus':[connectivityGyrus],
                                 'ConnectivityNameBN':[connectivityNameBN]})

                dataframe_dict.update(_dataframe_dict)


                # Add more atlas names (Target)
                if self.atlas_dict_list:
                    for idx, atlas_dict in enumerate(self.atlas_dict_list):
                        name = atlas_dict['name']
                        dataframe_dict['ConnectivityName'+name] = [connectivityName_list[idx]]

                _dataframe_dict = co.OrderedDict({
                                 'ConnectivityName':[underConnectivityName],
                                 'Connectivity_X':[connectivity_x],
                                 'Connectivity_Y':[connectivity_y],
                                 'connectivity_Z':[connectivity_z],
                                 'Under(-1)/Over(1)Connectivity':[-1]})


                dataframe_dict.update(_dataframe_dict)

                _df = pd.DataFrame(dataframe_dict)


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


                if read_hemis_from_csv:
                    if OverHem.upper() in ['L','R','C']:
                        hemisphereOC = OverHem.upper()
                    elif OverHem == '-':
                        hemisphereOC = self.get_hemisphere(overConnectedMNIint)
                    else:
                        raise Exception('Incorrect Hemisphere entry at UC MNI: ',overConnectedMNIint)
                else:
                    hemisphereOC = self.get_hemisphere(overConnectedMNIint)


                connectivity_x = overConnectedMNIint[0]
                connectivity_y = overConnectedMNIint[1]
                connectivity_z = overConnectedMNIint[2]

                # _,connectivityNameHO,_ = self.HOAtlasObj.getAtlasRegions(overConnectedMNIint)
                # _,connectivityNameJuliech,_ = self.JuliechAtlasObj.getAtlasRegions(overConnectedMNIint)

                # Loop over atlases (For target)
                if self.atlas_dict_list:
                    connectivityName_list = []
                    for atlas_dict in self.atlas_dict_list:
                        obj = atlas_dict['obj']
                        _, connectivityname, _ = obj.getAtlasRegions(overConnectedMNIint)
                        connectivityName_list.append(connectivityname)

                _,connectivityLobe, connectivityGyrus, connectivityNameBN = self.BNAtlasObj.getAtlasRegions(overConnectedMNIint)


                # Construct the dictionary in the loop and then make it a dataframe

                dataframe_dict = co.OrderedDict({
                                 'S_No': [s_no],
                                 'PaperID':[paperID],
                                 'SeedHemisphere':[hemisphereSeed],
                                 'SeedLobe':[seedLobe],
                                 'SeedGyrus':[seedGyrus],
                                 'SeedNameBN':[seedNameBN]})

                # Add more atlas names (Seed)
                if self.atlas_dict_list:
                    for idx, atlas_dict in enumerate(self.atlas_dict_list):
                        name = atlas_dict['name']
                        dataframe_dict['SeedName'+name] = [seedName_list[idx]]


                _dataframe_dict = co.OrderedDict({
                                 'SeedName':[seedName],
                                 'Seed_X':[seed_x],
                                 'Seed_Y':[seed_y],
                                 'Seed_Z':[seed_z],
                                 'ConnectivityHemisphere':[hemisphereOC],
                                 'ConnectivityLobe':[connectivityLobe],
                                 'ConnectivityGyrus':[connectivityGyrus],
                                 'ConnectivityNameBN':[connectivityNameBN]})

                dataframe_dict.update(_dataframe_dict)


                # Add more atlas names (Target)
                if self.atlas_dict_list:
                    for idx, atlas_dict in enumerate(self.atlas_dict_list):
                        name = atlas_dict['name']
                        dataframe_dict['ConnectivityName'+name] = [connectivityName_list[idx]]

                _dataframe_dict = co.OrderedDict({
                                 'ConnectivityName':[overConnectivityName],
                                 'Connectivity_X':[connectivity_x],
                                 'Connectivity_Y':[connectivity_y],
                                 'connectivity_Z':[connectivity_z],
                                 'Under(-1)/Over(1)Connectivity':[1]})


                dataframe_dict.update(_dataframe_dict)

                _df = pd.DataFrame(dataframe_dict)

                dat1 = dfExtra[ix:ix+1]
                dat2 = _df

                dat1 = dat1.reset_index(drop=True)
                dat2 = dat2.reset_index(drop=True)

                temp = pd.concat([dat1,dat2],axis=1)
                df_new = df_new.append(temp)




        cols=[
        'S_No','PaperID','SeedHemisphere','SeedLobe','SeedGyrus', 'SeedNameBN'
        ]

        if self.atlas_dict_list:
            for idx, atlas_dict in enumerate(self.atlas_dict_list):
                cols.append('SeedName'+atlas_dict['name'])

        cols.extend([
        'SeedName', 'Seed_X','Seed_Y','Seed_Z',
        'ConnectivityHemisphere','ConnectivityLobe',
        'ConnectivityGyrus','ConnectivityNameBN'])


        if self.atlas_dict_list:
            for idx, atlas_dict in enumerate(self.atlas_dict_list):
                cols.append('ConnectivityName'+atlas_dict['name'])

        cols.extend([
        'ConnectivityName', 'Connectivity_X', 'Connectivity_Y',
        'connectivity_Z', 'Under(-1)/Over(1)Connectivity'])



        df_new = df_new.loc[:,dfExtra.columns.append(pd.Index(cols))]


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

    # @staticmethod
    # def remove_duplicate_links(columns_index, in_file, out_file):
    #     """
    #     This function iterates through each link A-B and deletes the occurance
    #     of all the following links B-A.
    #
    #     Input: List Index of columns specifiying nodes A and B.
    #     Output: FIle with the duplicate links removed.
    #
    #     Algorithm:
    #     ---------
    #
    #     """
    #     df = pd.read_csv(in_file)
    #
    #     node_a_index = columns_index[0:math.floor(len(column_index)/2)]
    #     node_b_index = columns_index[math.floor(len(column_index)/2) + 1:]
    #
    #     for ix1, (Index, row1) in  tqdm(enumerate(df.iterrows())):
    #         for ix2, (Index, row2) in enumerate(df[ix1+1:].iterrows()):
    #             pass


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
                # print(row1[1], row2[1]) # printing S_no pairs
                # if all the columns match/ Same links
                node1 = {tuple(row1[_columns_match_index[0:math.floor(len(_columns_match_index)/2)]]), tuple(row1[_columns_match_index[math.floor(len(_columns_match_index)/2):]])}
                node2 = {tuple(row2[_columns_match_index[0:math.floor(len(_columns_match_index)/2)]]), tuple(row2[_columns_match_index[math.floor(len(_columns_match_index)/2):]])}
                # print('Node 1 and 2', node1, node2)
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
        Update: No Need of this function as we will introducing synthetic links
        using and then taking care of it using pivot tableself.
        Code to make all the same links have same end points so that they can
        be beneficial in the creating pivot table
        links_columns: The columns representing the Hemisphere and Names of the
        regions of both the link end points
        links_columns_all_details: The columns representing all the other
        details associated with the node such as
        MNI coordinates, names according to other atlases etc.

        Returns the ordered dataframe and saves the csv file

        Usage: className.order_links_end_points(in_file,links_columns,
                                                links_columns_all_details,
                                                out_file)
        links_columns_all_details: Divides this vector into 2 -
        source and destination details and then swaps them
        """

        df = pd.read_csv(in_file)#.iloc[:,1:]
        # links_columns =  [41,45,51,55]
        links_node_swapped_columns = links_columns[math.floor(len(links_columns)/2):] + \
                                     links_columns[0:math.floor(len(links_columns)/2)]


        # links_columns_all_details =  list(np.arange(41,61))
        links_node_swapped_columns_all_details = \
        links_columns_all_details[math.floor(len(links_columns_all_details)/2):] +\
        links_columns_all_details[0:math.floor(len(links_columns_all_details)/2)]


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

                        # print('swapped',ix1,ix1 + 1 +ix2)
                    # print('Row1', row1,'Row2', row2)
                    # import ipdb; ipdb.set_trace()



        df.to_csv(out_file, index=False)

        return df

    #TODO Test this function
    @staticmethod
    def add_synthetic_links(in_file,links_columns_all_details,out_file):
        """
        This function swaps the nodes of the links, creates new link and append the new links
        Input: in_file :CSV file containing links
               links_columns_all_details: The columns representing all the details associated with the node(seed,target) such as
               MNI coordinates, names according to other atlases etc.
               Name of the CSV file to be saved
        Output: Dataframe of the final csv with synthetic links
        """

        df = pd.read_csv(in_file)


        links_node_swapped_columns_all_details = links_columns_all_details[math.floor(len(links_columns_all_details)/2):] + links_columns_all_details[0:math.floor(len(links_columns_all_details)/2)]

        df_new = df.copy()

        for ix1, (Index, row1) in  tqdm(enumerate(df.iterrows())):
            temp = []
            for i in range(len(links_columns_all_details)):

                if i < math.floor(len(links_columns_all_details)/2):
                    temp.append(df.iat[ix1, links_columns_all_details[i]])
                    df_new.iat[ix1, links_columns_all_details[i]] = df.iat[ix1, links_node_swapped_columns_all_details[i]]
                else:
                    df_new.iat[ix1, links_columns_all_details[i]] = temp[i - math.floor(len(links_columns_all_details)/2)]

                print('swapped details of ',ix1)


        """
        Create new column denoting if a link is synthetic or not.
        """
        # Putting synthetic = 1 for the new links created
        df_new = df_new.assign(synthetic = np.ones(df_new.shape[0]))
        # Putting synthetic = 0 for the new links created
        df = df.assign(synthetic = np.zeros(df.shape[0]))

        df = df.append(df_new)

        """
        Appending the dataframe containing synthetic links (synthetic = 0)
        to the original dataframe with real links (synthetic = 0)
        """
        df.to_csv(out_file, index=False)

        return df

    @staticmethod
    def check_number_of_consistencies(in_file1, in_file2):
        """
        This function finds, across all the links of a study (file1), how many
        links are consistent. It refers to a list of consistent links (file2).

        in_file1: File that contains all the links of the study in question
        about consistency. It contains link name in each line.
        in_file2: File that contains all the consistent links for all studies.
        """

        consistentency_count = 0

        with open(in_file2,'r') as f2:
            for line2 in f2:
                link2 = line2.strip()
                with open(in_file1,'r') as f1:
                    for line1 in f1:
                        link1 = line1.strip()
                        if link2 == link1:
                            consistentency_count += 1
                            break

        return consistentency_count

    @staticmethod
    def find_ABIDE_links(in_file, all_links_col_idx, consistent_links_col_idx,
                        paperID_participant_col_idx,
                        out_file = 'link_participants.csv'):
        """
        Finds the links that has participants from the ABIDE dataset

        Input:
            in_file: CSV containg all the following columns
            all_links_col_idx: Columns containing the paperID, LinkName.
            consistent_links_col_idx: Columns containing LinkNames
            paperID_paticipant_col_idx: Columns containing paperID, Original/ABIDE
            out_file: Name of the output file

        Output:
            2 row file - Link and Original/ABIDE
        """

        df = pd.read_csv(in_file)

        all_links_df = df.iloc[:, all_links_col_idx]
        consistent_links_df = df.iloc[:, consistent_links_col_idx]
        paperID_participants_df = df.iloc[:, paperID_participant_col_idx]


        # Dict associating each paperID with Participants(original/ABIDE) from paperID_ABIDE_file
        dict_paperID_participants = {}
        for index, row in paperID_participants_df.iterrows():
            dict_paperID_participants[row['paperID2']] = row['participants2']

        # Dict associating each link with a list of Participants(original/ABIDE) from all_links_file
        dict_link_participants = {}
        for index, row in all_links_df.iterrows():
            if row['link1'] in dict_link_participants:
                dict_link_participants[row['link1']] = \
                dict_link_participants[row['link1']] + '; ' + str(row['paperID1']) \
                +'-'+ dict_paperID_participants[row['paperID1']]
            else:
                dict_link_participants[row['link1']] = \
                 str(row['paperID1']) +'-'+ dict_paperID_participants[row['paperID1']]


        # Now loop over each consistent link and using the previous dict, find
        # out the participant types
        df_link_participants = co.OrderedDict()
        for index, row in consistent_links_df.iterrows():
            if pd.isna(row['link2']):
                break
            if row['link2'] in df_link_participants:
                raise Exception('Duplicate consistent links found ', row['link2'])
            else:
                df_link_participants[row['link2']] = dict_link_participants[row['link2']]

        df_link_participants = pd.DataFrame(df_link_participants, index=[0])
        df_link_participants.to_csv(out_file, index = False)



def show_columns(df):
    """
    This function gives a quick viwe of what are the columns and their
    corresponding indices of a csv file or dataframe.
    It is quite handy while debugging.

    Input: CSV file path or a pandas Dataframe
    Output: Displays the columns along with their index

    """

    if isinstance(df,str):
        df = pd.read_csv(df)

    ind = np.arange(len(df.columns))

    for entry in zip(ind,df.columns):
        print(entry)


if __name__ == "__main__":

    REMOVE_BLANKS = False
    REMOVE_DUPLICATES =  False
    CONSISTENT_INCONSISTENT_LINKS = False
    SYNTHETIC_LINKS = True
    ORDER_LINK_NODES = False

    READ_HEMIS_FROM_CSV = True

    prob = True

    base_path = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/'


    if prob:
        atlas_paths = [
        base_path + 'hoAtlas/HarvardOxford-cort-prob-1mm.nii.gz',
        base_path + 'hoAtlas/HarvardOxford-sub-prob-1mm.nii.gz'
        # base_path + 'cerebellumAtlas/Cerebellum-MNIflirt-prob-1mm.nii.gz'
        ]
        atlasPath2 = [
        base_path + 'juelichAtlas/Juelich-prob-1mm.nii.gz'
        ]
        cerebellum_path = [
        base_path + 'cerebellumAtlas/Cerebellum-MNIflirt-prob-1mm.nii.gz'
        ]
        BN_atlas_path = 'brainnetomeAtlas/BNA-prob-2mm.nii.gz'


    else:
        atlas_paths = [
        base_path + 'hoAtlas/HarvardOxford-cort-maxprob-thr25-1mm.nii.gz',
        base_path + 'hoAtlas/HarvardOxford-sub-maxprob-thr25-1mm.nii.gz'
        # base_path + 'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz'
        ]
        atlasPath2 = [
        base_path + 'juelichAtlas/Juelich-maxprob-thr25-1mm.nii.gz'
        ]
        cerebellum_path = [
        base_path + 'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz'
        ]

        BN_atlas_path = base_path + 'brainnetomeAtlas/BNA-maxprob-thr25-1mm.nii.gz'

    atlas_labels_paths = [
    base_path + 'hoAtlas/HarvardOxford-Cortical.xml',
    base_path + 'hoAtlas/HarvardOxford-Subcortical.xml'
    # base_path + 'cerebellumAtlas/Cerebellum_MNIflirt.xml'
    ]
    atlasLabelsPath2 = [
    base_path + 'juelichAtlas/Juelich.xml'
    ]
    cerebellum_labels_path = [
    base_path + 'cerebellumAtlas/Cerebellum_MNIflirt.xml'
    ]

    BN_atlasRegionsDescrpPath = \
    base_path + 'brainnetomeAtlas/BNA_subregions_machineReadable.xlsx'

    BNAtlasObj = bu.queryBrainnetomeROI(BN_atlas_path, BN_atlasRegionsDescrpPath)

    HOAtlasObj = au.queryAtlas(atlas_paths,atlas_labels_paths)

    JuliechAtlasObj = au.queryAtlas(atlasPath2,atlasLabelsPath2)

    cerebellum_atlas_obj = au.queryAtlas(cerebellum_path,cerebellum_labels_path)

    aal_atlas_path = [base_path +
    'aalAtlas/AAL.nii.gz']
    aal_atlas_labels_path = [base_path +
    'aalAtlas/AAL.xml']

    aal_atlas_obj = au.queryAtlas(aal_atlas_path,aal_atlas_labels_path, atlas_xml_zero_start_index = False )

    Schaefer_atlasPath = [
    base_path + 'Schaefer_4d_Atlas_7_Networks.nii.gz']
    Schaefer_atlasLabelsPath = [
    base_path + 'schaeferAtlas/Schaefer_4d_Atlas_7_Networks_1mm.xml']

    SchaeferAtlasObj = au.queryAtlas(Schaefer_atlasPath, Schaefer_atlasLabelsPath)


    csvPath = 'csv_input/als.csv'
    # q = addAtlasNamestoCSV(BNAtlasObj, HOAtlasObj, JuliechAtlasObj)


    # ------------------------Atlas dictionary--------------------------------
    HO_atlas_dict = {'obj': HOAtlasObj, 'name': 'HO'}
    cerebellum_atlas_dict = {'obj': cerebellum_atlas_obj, 'name': 'CBLM'}
    juliech_atlas_dict = {'obj': JuliechAtlasObj, 'name':'Juliech'}
    BNA_atlas_dict = {'obj': BNAtlasObj, 'name':'BN'}
    aal_atlas_dict = {'obj': aal_atlas_obj, 'name':'AAL'}
    schaefer_atlas_dict = {'obj': SchaeferAtlasObj, 'name':'Schaefer'}
    atlas_dict_list = [HO_atlas_dict, cerebellum_atlas_dict, aal_atlas_dict, juliech_atlas_dict,schaefer_atlas_dict]
    # atlas_dict_list = [HO_atlas_dict, juliech_atlas_dict]

    # ------------------------------------------------------------------------

    q = addAtlasNamestoCSV(BNA_atlas_dict, atlas_dict_list)


    # columns_index_include = [0,1,28,29,30,31]

    # columns_index_include = [0,1]
    # columns_index_include.extend(list(np.arange(3,41)))

    columns_index_include = list(np.arange(3,41))

    filename = 'csv_output/finalLinks_all_columns.csv'
    df = q.addNameCSV(csvPath, filename, columns_index_include, READ_HEMIS_FROM_CSV)

    # Remove the blank links

    if REMOVE_BLANKS:
        in_file = 'csv_output/finalLinks_all_columns.csv'
        out_file = 'csv_output/finalLinks_blanks_dropped_all_columns.csv'
        dropped_file = 'csv_output/dropped_all_columns.csv'

        column_index = [44,54]
        df_final, df_dropped = addAtlasNamestoCSV.remove_blank_links(column_index,in_file,out_file,dropped_file)
        in_file = 'csv_output/finalLinks_blanks_dropped_all_columns.csv'

    else:
        in_file = 'csv_output/finalLinks_all_columns.csv'


    # Remove Duplicates

    # Remove Duplicates: For each paper ID independently, remove the link that has same hemisphere HO region
    # as source and target and that has same connectivity value


    if REMOVE_DUPLICATES:
        out_file = 'csv_output/finalLinks_duplicates_removed_all_columns.csv'

        column_index = [39,40,44,50,54,60]

        df_extracted = addAtlasNamestoCSV.remove_duplicate_rows(column_index,in_file,out_file)
        in_file = 'csv_output/finalLinks_duplicates_removed_all_columns.csv' # For next Step


    import pdb;pdb.set_trace()


    # ------------------------------------
    # Include synthetic link
    if SYNTHETIC_LINKS:
        print('Creating synthetic links')

        """
        Every new atlas added will increase the end_range (2nd term of np.range) by 2. By default (i.e.)
        only with BNA, the range will be (40,56). With HO and Juliech added, the
        range becomes (40,60). Now with added cerebellum the range should be
        (40,62)
        """
        range_end = 56 + 2 * len(atlas_dict_list)

        links_columns_all_details =  list(np.arange(40, range_end))

        out_file = 'csv_output/finalLinks_synthetic_added_all_columns.csv'
        df = addAtlasNamestoCSV.add_synthetic_links(in_file,links_columns_all_details,out_file)
        in_file = 'csv_output/finalLinks_synthetic_added_all_columns.csv' # For next Step


    # -----------------------------------

    # Order the link nodes
    if ORDER_LINK_NODES:
        # Code to make all the same links have same end points so that they can be beneficial in the creating pivot table
        # in_file = 'csv_output/finalLinks_duplicates_removed_all_columns.csv'
        out_file = 'csv_output/finalLinks_duplicates_removed_ordered_all_columns_incl_networks.csv'
        # links_columns =  [41,45,51,55]
        links_columns =  [40,44,50,54]

        links_columns_all_details =  list(np.arange(40,60))

        df_ordered = addAtlasNamestoCSV.order_links_end_points(in_file,links_columns,links_columns_all_details,out_file)



    # Consistent and conflicting links

    # Match the rows having same hemisphere and same HO region

    columns_match_index = [40,44,50,54]

    connectivity_column_index = [60]
    s_no_column_index = [38]
    paper_id_column_index = [39]


    if CONSISTENT_INCONSISTENT_LINKS:
        # TODO exchange df_extracted by file name
        df_conflicts_details, df_consistent_details = addAtlasNamestoCSV.find_consistent_conflicting_links(df_extracted, columns_match_index, connectivity_column_index,\
        s_no_column_index, paper_id_column_index, ignore_hemispheres = False)
