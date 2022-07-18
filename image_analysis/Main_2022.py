# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 13:18:47 2022

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
from processing.processing_functions import temporal_mean_filter, save_imgs, temporal_median_filter, open_images, binarize_imgs, correct_background, select_ROI, invert_imgs, mask_ROIs
from analysis.Analyse_results_with_connected_components import Measure
import cv2
#from analysis.Select_ROI import execute_roi
#from AcquireAndSave import execute_capture
#from AcquireAndDisplay import execute_focus


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
ROIs = select_ROI(ROI_PATH) 
#TODO: close image


#%%
## PRE-PROCESSING IMAGES
print('Original images shape: ', np.shape(imgs))

# 1. Temporal average filter: to remove moving objects
window_size = 5
imgs_avg = temporal_mean_filter(imgs, window_size)
print('Averaged images shape: ', np.shape(imgs_avg))
#imgs_median = temporal_median_filter(imgs, window_size)

# 2. Background illumination intensity correction
imgs_corrected = correct_background(imgs_avg, ORIGINAL_FOLDER)  #TODO: WARNING IMGS_AVG
print('Corrected images shape: ', np.shape(imgs_corrected))

# 3. Inverting image (our AU-NP spots will be white ~255)
imgs_inv = invert_imgs(imgs_corrected)
print('Inverted images shape: ', np.shape(imgs_inv))

# 4. Binarizing images: we will have a binary image based on a threshold
#rets, imgs_thresh = binarize_imgs(imgs_inv, tr = 225)
#blur = cv2.GaussianBlur(imgs_inv,(5,5),0)
ret3,imgs_thresh = cv2.threshold(imgs_inv,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
print('Thresholded images shape: ', np.shape(imgs_thresh))



