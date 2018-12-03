
# coding: utf-8

# # Adjecency matrix to edgelist

# In[2]:


import pandas as pd
import numpy as np


# In[44]:


adjmatrix_path_list = ['csv_input/DMN_underconnectivity.csv', 'csv_input/DMN_overConnectivity.csv']
connectivity_list = [-1,1]


# In[ ]:





# In[ ]:





# In[45]:


for ix, adjmatrix_path in enumerate(adjmatrix_path_list):
    df = pd.read_csv(adjmatrix_path)
    seed_regions = df.iloc[:,0].as_matrix()
    target_regions = list(df.columns)[1:]
    matrix = df.iloc[:,1:].as_matrix()
    # seed_regions
    # print("%5s , %5s , %5s"%('ROI_1','ROI_2','Strength','Connectivity'))
    for row_ix, seed in enumerate(seed_regions):
        for col_ix, target in enumerate(target_regions):
    #         print(seed,target)
            strength = matrix[row_ix,col_ix]
            if np.isnan(strength):
                strength = 0
            print("%s , %s , %f, %f"%(seed,target,strength, connectivity_list[ix]))


# In[37]:






# In[ ]:
