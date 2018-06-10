#!/bin/sh

#cd <folderContainingFiles>

#% The files need to be in 2mm

#% Thresholding the -log(qval) file at 1.3. Note that the file will be in 2mm

echo Thresholding
fslmaths map_logq_2mm.nii.gz -thr 1.3 qvalLogPosThr 
fslmaths map_logq_2mm.nii.gz  -mul -1 -thr 1.3 qvalLogNegThr 

#% After Thresholding, you need to binarise the mask. I think this can be done in the previous step also.

echo Binarizing
fslmaths qvalLogPosThr -bin qvalLogPosMask
fslmaths qvalLogNegThr -bin qvalLogNegMask



#% After creating the masks, you need to multiply these masks with t-values. This is because we would be clustering on t-values and not on q-values.

echo Multiplying mask with t-values
fslmaths Tvals_2mm.nii.gz -mul qvalLogPosMask.nii.gz tValPosThr
fslmaths Tvals_2mm.nii.gz -mul qvalLogNegMask.nii.gz tValNegThr

#% Here, we will split the above created files

# Making the negative t values positive

fslmaths tValNegThr -abs tValNegThrAbs

echo splitting
fslsplit tValPosThr.nii.gz split_tValPosThrRoi/tValPosThrRoi
fslsplit tValNegThrAbs.nii.gz split_tValNegThrRoi/tValNegThrRoi

echo Creating cortical and subcortical mask

fslmaths BNA-maxprob-thr0-2mm.nii.gz -bin BNA-maxprob-thr0-2mm-Mask.nii.gz

echo applying cluster command

for i in `seq -f %04g 0 246` 
 	do
		
		fslmaths split_tValPosThrRoi/tValPosThrRoi$i".nii.gz" -mul BNA-maxprob-thr0-2mm-Mask.nii.gz split_tValPosThrRoi/tValPosThrRoi$i".nii.gz"
		fslmaths split_tValNegThrRoi/tValNegThrRoi$i".nii.gz" -mul BNA-maxprob-thr0-2mm-Mask.nii.gz split_tValNegThrRoi/tValNegThrRoi$i".nii.gz"
 
 		cluster --in=split_tValPosThrRoi/tValPosThrRoi$i".nii.gz"  --thresh=0.00001 > clustersHyperConnected/tValPosThrRoi$i'_cluster.txt' --mm
		cluster --in=split_tValNegThrRoi/tValNegThrRoi$i".nii.gz"  --thresh=0.00001 > clustersHypoConnected/tValNegThrRoi$i'_cluster.txt' --mm
done


# echo  $i ${rois[$j]} $j



