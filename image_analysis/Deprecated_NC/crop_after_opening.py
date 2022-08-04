# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:06:13 2022

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
from processing.processing_functions import *
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
print('/n Files to be processed in ', IMG_PATH)
NAME_IMG_FOLDER = os.path.basename(IMG_PATH)

# 2. Select image to use for placing the ROIs
root = Tk()
root.withdraw()
ROI_PATH = os.path.abspath(filedialog.askopenfilename(title='Select image to place ROI ', initialdir = IMG_PATH))
print('\n Selected image to place ROI ', ROI_PATH)

import os 
from scipy import misc 


#%%

## SELECT ROI
ROIs = select_ROI_NC(ROI_PATH,5472, 3648, 500 ) 
#TODO: close image



#%%
from imageio import imread

#%%

img= imread("C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/images_lab3/kohler1.bmp")

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
spot = clahe.apply(img[:, :])
#bg = clahe.apply(roi_cropped2[:, :])
list1 = []
list2 = []
list1.append(spot)
#list2.append(bg)


#%%

ret, thresh1 = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# Remove hair with opening
kernel = np.ones((5,5),np.uint8)
opening = cv2.morphologyEx(thresh1,cv2.MORPH_OPEN,kernel, iterations = 1) #original code had 2 iterations


# ret_gb, thresh_bg = cv2.threshold(roi_cropped2,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# kernel2 = np.ones((6,6),np.uint8)
# # Remove hair with opening
# opening_bg = cv2.morphologyEx(thresh_bg,cv2.MORPH_OPEN,kernel2, iterations = 2) #original code had 2 iterations


list1.append(thresh1)
list1.append(opening)
# list2.append(thresh_bg)
# list2.append(opening_bg)

#%%

indx1 = ROIs[0][0]-500
indx2 = ROIs[0][0]+500
indx3 = ROIs[0][1]-500
indx4 = ROIs[0][1]+500

indx1_2 = ROIs[1][0]-500
indx2_2 = ROIs[1][0]+500
indx3_2 = ROIs[1][1]-500
indx4_2 = ROIs[1][1]+500

spot = opening[indx3:indx4, indx1:indx2]
bg = opening[indx3_2:indx4_2, indx1_2:indx2_2]

list1.append(spot)
list2.append(bg)
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

h, w = spot.shape[:2]
mask = create_circular_mask(h, w, 350)
masked_img = spot.copy()
masked_img[~mask] = 0

masked_bg = bg.copy()
masked_bg[~mask] = 0

list1.append(masked_img)
list2.append(masked_bg)



#%%
num_white = cv2.countNonZero(masked_img)  
num_white_bg = cv2.countNonZero(masked_bg)
blank = np.zeros([800,800],dtype=np.uint8)
blank.fill(255)
blank[~mask] = 0
#%%
num_white_mask = cv2.countNonZero(blank) 

signal = (num_white - num_white_bg)/num_white_mask * 100
signal2 = (num_white)/num_white_mask * 100


print('The pixel ratio inside the ROI is ', signal)
print('The pixel ratio inside the ROI without background subtraction is ', signal2)