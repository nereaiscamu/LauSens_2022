# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 17:40:21 2022

@author: nerea
"""
import sys 
import os

#path_code = os.path.dirname(__file__)

#important to import file that are not here
#sys.path.append(os.path.abspath(path_code))

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk
from PIL import Image
from processing.processing_functions import * #temporal_mean_filter, save_imgs, temporal_median_filter, open_images, binarize_imgs, correct_background, select_ROI, invert_imgs, mask_ROIs
from analysis.Analyse_results_with_connected_components import Measure
import cv2
from random import randint
import numpy.matlib
from numpy.random import default_rng

#%%
## OPENING FILES
ORIGINAL_FOLDER = os.path.dirname(os.path.realpath(__file__))
print('THIS IS ORIGINAL FOLDER PATH', str(ORIGINAL_FOLDER))
IMG_FOLDER = os.path.join('images') #Folder where the images taken by the camera to be processed will be located
IMG_PROCESSED_FOLDER = os.path.abspath('images_processed')  #Folder where the resulting images will be located


# 1. Select folder with images
root = Tk()
root.withdraw()
IMG_PATH = os.path.abspath(filedialog.askdirectory( title='Select Folder with images to be analyzed', initialdir = IMG_FOLDER))
print('\n Files to be processed in ', IMG_PATH)
NAME_IMG_FOLDER = os.path.basename(IMG_PATH)

# 2. Select image to use for placing the ROIs
root = Tk()
root.withdraw()
ROI_PATH = os.path.abspath(filedialog.askopenfilename(title='Select image to place ROI ', initialdir = IMG_PATH))
print('\n Selected image to place ROI ', ROI_PATH)


# 3. Loading images in directory folder
imgs, time_creation = open_images(IMG_PATH)
print('Shape imgs', np.shape(imgs))
framerate = np.mean(np.diff(time_creation))
os.chdir(ORIGINAL_FOLDER)

#%%
## SELECT ROI
ROIs = select_ROI_NC(ROI_PATH) 
#TODO: close image

#%%
'''Method for linear fit and background correction from here:
    https://de.mathworks.com/matlabcentral/answers/45680-faster-method-for-polyfit-along-3rd-dimension-of-a-large-3d-matrix#answer_55902
    '''
newarray = np.dstack(imgs)
size = np.shape(newarray)
rng = default_rng(42)
num = size[2]
x = rng.random(num)



#%%
z = 1 # first degree polynomial
V =  np.c_[np.ones((num, 1)), np.cumprod((np.matlib.repmat(x, 1, z).reshape(z,num).T), 1)]
M = V.dot(np.linalg.pinv(V))

#%%

p1 = np.transpose(newarray, (2, 0, 1))
p1 = p1.reshape(size[2], size[0]*size[1])
polyCube = M.dot(p1)
polyCube = np.reshape(polyCube,(size[2], size[0],size[1]));
polyCube = np.transpose(polyCube,[1, 2, 0]);

imgs_poly = []

for i in np.arange(0,num):
    imgs_poly.append(polyCube[:,:,i])
    
# 3. Inverting image (our AU-NP spots will be white ~255)

imgs_inv = np.invert(imgs_poly[-1].astype(np.uint8))
print('Inverted images shape: ', np.shape(imgs_inv))

imgs_inv2 = []
imgs_inv2.append(imgs_inv)

#%%

#blur = cv2.GaussianBlur(imgs_inv,(5,5),0)
#ret3,imgs_thresh = cv2.threshold(imgs_poly[-1].astype(np.uint8),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
ret3,imgs_thresh = cv2.threshold(imgs_inv,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
print('Thresholded images shape: ', np.shape(imgs_thresh))

imgs_t2 = []
imgs_t2.append(imgs_thresh)


#%%
# Original image

# Circular ROI in original image; must be selected via an additional mask
roi = np.zeros(imgs_thresh.shape[:2], np.uint8)
roi = cv2.circle(roi, (ROIs[0,0], ROIs[0,1]), ROIs[0,2], 255, cv2.FILLED)



#%%
# Target image; white background
mask = np.ones_like(imgs_thresh) * 255


# Copy ROI part from original image to target image
mask = cv2.bitwise_and(mask, imgs_thresh, mask=roi) + cv2.bitwise_and(mask, mask, mask=~roi)

#%%
masks = []
masks.append(mask)


mask_inv = np.invert(mask.astype(np.uint8))
masks_inv = []
masks_inv.append(mask_inv)


num_white = cv2.countNonZero(mask_inv)  

area_Roi = np.pi*ROIs[0,2]**2

signal = (area_Roi - num_white)/area_Roi * 100

print('The pixel ratio inside the ROI is ', signal)