import numpy as np

import brainnetomeUtility as bu
import atlasUtility as au
import argparse

# -----------------------------------------------------------------------------
# TODO To go in config.json file
# -----------------------------------------------------------------------------
atlas_path = ('/home/varun/Projects/fmri/Autism-survey-connectivity-links-'
              'analysis/brainnetomeAtlas/BNA-prob-2mm.nii.gz')
atlasRegionsDescrpPath = ('/home/varun/Projects/fmri/Autism-survey-'
                          'connectivity-links-analysis/brainnetomeAtlas/'
                          'BNA_subregions_machineReadable.xlsx')

atlasPaths1  = [('/home/varun/Projects/fmri/Autism-survey-connectivity-links-'
                 'analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'),\
                ('/home/varun/Projects/fmri/Autism-survey-connectivity-links-'
                'analysis/hoAtlas/HarvardOxford-cort-maxprob-thr0-1mm.nii.gz'),\
                ('/home/varun/Projects/fmri/Autism-survey-connectivity'
                '-links-analysis/cerebellumAtlas/Cerebellum-MNIflirt-'
                'maxprob-thr0-1mm.nii.gz')]

atlasLabelsPaths1 = [('/home/varun/Projects/fmri/Autism-survey-connectivity-'
                     'links-analysis/hoAtlas/HarvardOxford-Subcortical.xml'),\
                     ('/home/varun/Projects/fmri/Autism-survey-connectivity-'
                     'links-analysis/hoAtlas/HarvardOxford-Cortical.xml'), \
                     ('/home/varun/Projects/fmri/Autism-survey-connectivity-'
                     'links-analysis/cerebellumAtlas/Cerebellum_MNIflirt.xml')]

# -----------------------------------------------------------------------------

# Parser to parse commandline arguments

ap = argparse.ArgumentParser()

ap.add_argument("-a", "--atlas", required=True,
                help="b: BN Atlas, hoc: HO/Cerebellum Atlas")
ap.add_argument("-mni", "--mni", nargs='+', required=True,
                help="MNI Coordinates space seperated")

args = vars(ap.parse_args())

# Reading the arguments

atlas = args["atlas"]
# Converting the numbers read as string to integers
MNI = list(map(int, args["mni"]))

# Temporary variables to be used as proxy for objects

q = q1 = False

if atlas == 'b':
    q = bu.queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath, True)
elif atlas == 'hoc':
    q1 = au.queryAtlas(atlasPaths1,atlasLabelsPaths1,False)
else:
    raise Exception('Incorrect Atlas Option')

# Assigning the proxy to the object variable

if q:
    obj = q
elif q1:
    obj = q1

# Get the region from the above defined atlas
print(obj.getAtlasRegions(MNI))
cont = True
while(cont):
    MNI = input('Type space seperated MNI (Or Type q to quit): ')
    if MNI == 'q':
        cont = False
        continue

    # Converting the numbers read as string to integers
    MNI = list(map(int, MNI.split()))
    print(obj.getAtlasRegions(MNI))
