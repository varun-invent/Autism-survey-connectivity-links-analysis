import subprocess
import resultsConsistencyCheck

shellScript = "creatingTable.sh"

cmd = "./" + shellScript

p1 = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

out1 = p1.communicate()


#TODO

'''
1. Read literature results sheet
2. Read SeedMNI, VoxelMNI
3. Find ROI number of SeedMNI in Brainnetome
4. Find ROI number of VoxelMNI in HO Cortical/subcortical Atlas and find the number/density of significant voxels I got in that ROI.
5. Report the follwoing:
    * SeedName SeedMNI SeedNameHO VoxelMNIName VoxelMNINameHO VoxelMNI (For Both under and over connected)

'''

resultsConsistencyCheck

class check()
