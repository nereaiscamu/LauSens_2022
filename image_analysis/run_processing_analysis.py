#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN PRE-PROCESSING AND ANALYSIS

From saved images taken by SensUs 2021 device (SPR on AU-NHA)

Created on Sun Aug 22 11:12:06 2021

@author: janet


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
rets, imgs_thresh = binarize_imgs(imgs_inv, tr = 225)
print('Thresholded images shape: ', np.shape(imgs_thresh))

# 5. Applying a mask with the ROIs
#imgs_masked = mask_ROIs(imgs_thresh, ROIs)
#print('Masked images shape: ', np.shape(imgs_masked))
# TODO: NOT USING IT FOR THE MOMENT


# View preprocessing
#idx = -1
#a = [imgs_avg[idx], imgs_corrected[idx], imgs_inv[idx], imgs_thresh[idx], imgs_masked[idx]]
#titles = ["Avg", 'Background correction', 'inverted','binarized', 'mask ROI']
#
#fig, axes = plt.subplots(2,3)
#for i, ax in enumerate(axes.flat):
#    try:
#        c = ax.imshow(a[i], cmap='gray')
#        fig.colorbar(c, ax = ax)
#        ax.set_title(titles[i])
#    except:
#        continue
#plt.show()


#%%
# ANALYZING IMAGES
signal = []
foreground = []
background = []

capture_refresh_time = framerate
for img in imgs_thresh:
    mes = Measure(NAME_IMG_FOLDER, ROIs, capture_refresh_time)
    result = mes.signal_perImage(img)
    signal = result[0]
    foreground = result[1]
    background = result[2]
    print('final signal', signal)

# Saving result in npy and csv
with open('result.npy', 'wb') as f:
    np.save(f, result)
np.savetxt("result.csv", result)
    
    

plt.figure()
time = np.arange(0, len(signal)*framerate*window_size, framerate*window_size)
plt.plot(time, signal)
plt.show()


#%%
# Saving
SAVING_FOLDER = os.path.join(IMG_PROCESSED_FOLDER, NAME_IMG_FOLDER)
saving = True
if saving == True :
    save_imgs(imgs_avg, SAVING_FOLDER, NAME_IMG_FOLDER+'_avg_') # saving in a folder with the name of the original one but inside /images_processed
    #save_imgs(imgs_median, SAVING_FOLDER, NAME_IMG_FOLDER+'_median_')



#%% To save/open the arrays (because my computer is too slow)
#par = np.array([imgs, imgs_avg, NAME_IMG_FOLDER, ROIs, ROI_PATH, IMG_PATH], dtype=object)
#with open('test.npy', 'wb') as f:
#    np.save(f, par)

open_saved_data = True
if open_saved_data == True:
    with open('./test.npy', 'rb') as f:
        par = np.load(f, allow_pickle=True)
    [imgs, imgs_avg, NAME_IMG_FOLDER, ROIs, ROI_PATH, IMG_PATH] = list(par)

