# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 14:15:37 2022

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
img_raw = imgs[0]

indx1 = ROIs[0][0]-400
indx2 = ROIs[0][0]+400
indx3 = ROIs[0][1]-400
indx4 = ROIs[0][1]+400

indx1_2 = ROIs[1][0]-400
indx2_2 = ROIs[1][0]+400
indx3_2 = ROIs[1][1]-400
indx4_2 = ROIs[1][1]+400

roi_cropped = img_raw[indx3:indx4, indx1:indx2]
roi_cropped2 = img_raw[indx3_2:indx4_2, indx1_2:indx2_2]
list1 = []
list2 = []
list1.append(roi_cropped)
list2.append(roi_cropped2)

#%%
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
spot = clahe.apply(roi_cropped[:, :])
bg = clahe.apply(roi_cropped2[:, :])
equalized = np.dstack((spot))

list1.append(spot)
list2.append(bg)


#%%

ret, thresh1 = cv2.threshold(roi_cropped,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# Remove hair with opening
kernel = np.ones((5,5),np.uint8)
opening = cv2.morphologyEx(thresh1,cv2.MORPH_OPEN,kernel, iterations = 1) #original code had 2 iterations


ret_gb, thresh_bg = cv2.threshold(roi_cropped2,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
kernel2 = np.ones((6,6),np.uint8)
# Remove hair with opening
opening_bg = cv2.morphologyEx(thresh_bg,cv2.MORPH_OPEN,kernel2, iterations = 2) #original code had 2 iterations


list1.append(thresh1)
list1.append(opening)
list2.append(thresh_bg)
list2.append(opening_bg)
#%%

# Original image

# Circular ROI in original image; must be selected via an additional mask
roi = np.zeros(opening.shape[:2], np.uint8)
roi = cv2.circle(roi, (ROIs[0,0], ROIs[0,1]), ROIs[0,2], 255, cv2.FILLED)



#%%
def create_circular_mask(h, w, radius, center=None):
    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])
        
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask

h, w = opening.shape[:2]
mask = create_circular_mask(h, w, 350)
masked_img = opening.copy()
masked_img[~mask] = 0

masked_bg = opening_bg.copy()
masked_bg[~mask] = 0

list1.append(masked_img)
list2.append(masked_bg)



#%%
num_white = cv2.countNonZero(masked_img)  
num_white_bg = cv2.countNonZero(masked_bg)
blank = np.zeros([800,800],dtype=np.uint8)
blank.fill(255)
blank[~mask] = 0
list1.append(blank)
#%%
num_white_mask = cv2.countNonZero(blank) 

signal = (num_white - num_white_bg)/num_white_mask * 100
signal2 = (num_white)/num_white_mask * 100


print('The pixel ratio inside the ROI is ', signal)
print('The pixel ratio inside the ROI without background subtraction is ', signal2)
# #%%

# # Combine surrounding noise with ROI
# kernel = np.ones((3,3),np.uint8)
# dilate = cv2.dilate(opening,kernel,iterations=2)

# # Blur the image for smoother ROI
# blur = cv2.blur(dilate,(15,15))

# # Perform another OTSU threshold and search for biggest contour
# ret, thresh2 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


# list1.append(dilate)
# list1.append(thresh2)

# #%%
# contours, hierarchy = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# cnt = max(contours, key=cv2.contourArea)


# #%%¡¡

# # Create a new mask for the result image
# h, w = roi_cropped.shape[:2]
# mask = np.zeros((h, w), np.uint8)

# # Draw the contour on the new mask and perform the bitwise operation
# cv2.drawContours(mask, [cnt],-1, 255, -1)
# res = cv2.bitwise_and(roi_cropped, roi_cropped, mask=mask)

# list1.append(res)

# #%%

# # Display the result
# cv2.imshow('img', res)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# #%%
# f = roi_cropped
# # loop over images and estimate background 

# avg1 = np.float32(roi_cropped)
# avg2 = np.float32(roi_cropped)

# cv2.accumulateWeighted(f,avg1,1)
# cv2.accumulateWeighted(f,avg2,0.5)

# res1 = cv2.convertScaleAbs(avg1)
# res2 = cv2.convertScaleAbs(avg2)

# list1.append(res1)
# list1.append(res2)

