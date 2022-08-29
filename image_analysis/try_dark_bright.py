# -*- coding: utf-8 -*-

"""
Created on Mon Aug 29 00:23:09 2022

@author: nerea
"""
import sys 
import os
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk
from PIL import Image
from processing.processing_functions import *
from analysis.Analyse_results_with_connected_components import Measure
import cv2
from Nc_functions import *
from sklearn.linear_model import LinearRegression
from skimage import exposure

brightfield = cv2.imread('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/brightfield.png', cv2.IMREAD_GRAYSCALE)
darkfield = cv2.imread('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/darkfield.png', cv2.IMREAD_GRAYSCALE)
img = cv2.imread("C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/Images_Lab4/900pgml_sam_1/saved_img_056-0timestamp_652.8.jpeg", cv2.IMREAD_GRAYSCALE)


specimen = img
img_corrected = ((specimen - darkfield) / (brightfield - darkfield) )* 255

#img_corrected = np.array(255 * ( (specimen - brightfield)/(brightfield - darkfield)).astype(np.uint8))
#Normalizing the result
img_corrected_norm = np.array((img_corrected-img_corrected.min()) / (img_corrected.max()-img_corrected.min()) * 255, dtype=np.uint8)
#img_corrected_norm.astype(np.uint8)
ddepth = cv2.CV_16S
kernel_size = 5
log_list = []
src_gray = cv2.GaussianBlur(img_corrected, (3, 3), 0)
dst = cv2.Laplacian(src_gray, ddepth, ksize=kernel_size)
abs_dst = cv2.convertScaleAbs(dst)
plt.imshow(abs_dst)
#%%

src_gray2 = cv2.GaussianBlur(img, (3, 3), 0)
dst2 = cv2.Laplacian(src_gray2, ddepth, ksize=kernel_size)
abs_dst2 = cv2.convertScaleAbs(dst2)
plt.imshow(abs_dst2)

#%%
#ret, img_thresh = cv2.threshold(abs_dst, 160, 255, cv2.THRESH_BINARY)
ret1, img_thresh = cv2.threshold(abs_dst,0,255,cv2.THRESH_OTSU)
#ret, img_thresh = cv2.threshold(abs_dst, ret1, 255, cv2.THRESH_BINARY)


plt.imshow(img_thresh)

#%%
ret2, thresh2 = cv2.threshold(abs_dst2,0,255,cv2.THRESH_OTSU)
ret, img_thresh = cv2.threshold(abs_dst, ret2+70, 255, cv2.THRESH_BINARY)
plt.imshow(thresh2)

#%%
ret, img_thresh3 = cv2.threshold(img_corrected, 0,255,cv2.THRESH_OTSU)
plt.imshow(img_thresh3)


#%%
plt.imshow(img*(brightfield/2))