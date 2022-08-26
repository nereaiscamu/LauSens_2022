#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:03:53 2022

@author: camille
"""

#path_code = os.path.dirname(__file__)
#important to import file that are not here
#sys.path.append(os.path.abspath(path_code))
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

#from analysis.Select_ROI import execute_roi
#from AcquireAndSave import execute_capture
#from AcquireAndDisplay import execute_focus

#from skimage import (
#    data, restoration, util
#)
from cv2_rolling_ball import subtract_background_rolling_ball

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
imgs = open_images_NC(IMG_PATH)
print('Shape imgs', np.shape(imgs))
os.chdir(ORIGINAL_FOLDER)


#%%
n_spots = 2#input("How many spots are visible? ")
n_bg = 2#input("How many background regions to use? ")
n_ROIs =int(n_spots) + int(n_bg)
ROIs = Select_ROI_Dynamic(ROI_PATH, n_ROIs, scale_f = 4 )

width = height = int(ROIs[0,2]*2.5)
radius = ROIs[0][2]

#%% Plotting 
option_rollingball = True
plt.imshow(imgs[0], cmap='gray')
plt.title('initial image')
plt.show()

#%% Temporal median (remove moving particles)
avgd = imgs#temporal_median_filter(imgs, size_kernel_=5)

plt.imshow(avgd[0], cmap='gray')
plt.title('avgd image')
plt.show()
#%% Remove background 

'''inv_imgs = invert_imgs(imgs)
plt.imshow(inv_imgs[0])
plt.title('inverted image')
plt.show()'''

#smoothed = smooth_background(inv_imgs)
'''if option_rollingball:
    smoothed = []
    for img in imgs:
        #background = restoration.rolling_ball(img)
        #img_corrected = img-background
        

        
        # 277.076 s
        #t200_start = process_time() 
        img_corrected, background = subtract_background_rolling_ball(img, 50, light_background=True,
                             use_paraboloid=False, do_presmooth=False)
        #t200_end = process_time() 
        #print(f'Basic Time rolling ball 200 {t200_end-t200_start:.3f}.')
        
        smoothed.append(img_corrected)
else:
    smoothed = smooth_background(avgd)


plt.imshow(smoothed[0], cmap='gray')
plt.title('after bg cancellation image')
plt.show()'''

#%% Processing: extract pixel ratio
open_imgs_ = opening(avgd, iterations = 1)
print('after opening')
open_imgs = thresh_Otsu_Bin(open_imgs_)
print('after otsu')
import cv2

'''ret,thresh1 = cv2.threshold(smoothed[0],210,255,cv2.THRESH_BINARY)

plt.imshow(thresh1, cmap='gray')
plt.show()'''

plt.imshow(open_imgs_[0], cmap='gray')
plt.title('after opening image')
plt.show()

plt.imshow(open_imgs[0], cmap='gray')
plt.title('final image')
plt.show()

#bin_imgs = thresh_Otsu_Bin(open_imgs)
masks = create_circular_mask(open_imgs, radius, ROIs)
masked_imgs = apply_mask(open_imgs, masks)
result = pixel_ratio(masked_imgs, masks, n_spots, n_ROIs)
slope, R2 = linear_model(result)

img_test = open_imgs[0]
connectivity = 8  # You need to choose 4 or 8 for connectivity type
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img_test , connectivity , cv2.CV_32S)
nb_pixels = 0
for c in range(0, num_labels):
    if c == 0:
        #print("background")
        continue
    else:
        #print("Signal")
        area = stats[c, cv2.CC_STAT_AREA]
        if((area>3) & (area<30)): #TODO: before it was 9, 90
            nb_pixels = nb_pixels + area 
            
labels_img = Image.fromarray(labels)            
labels_img.show()             
percent_pixels = nb_pixels / stats[0, cv2.CC_STAT_AREA]
print(percent_pixels)