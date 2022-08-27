# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 16:27:53 2022

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

imgs_med = temporal_median(imgs, 5)

#%%
#works well at 800
circle = Select_ROI_Dynamic(ROI_PATH, 1, scale_f = 4 )
imgs_crop = crop_imgs_fixed(imgs_med, circle)
# plt.imshow(imgs_crop[4], cmap = 'gray')

#%%
n_spots = input("How many spots are visible? ")
n_bg = input("How many background regions to use? ")
n_ROIs =int(n_spots) + int(n_bg)
img = imgs_crop[-1]
ROIs = Select_ROI_Dynamic_crop(img, n_ROIs)

#%%
imgs_inv = invert_imgs(imgs_crop)
imgs_log = LoG(imgs_inv)
# plt.imshow(imgs_log[-1], cmap = 'gray')
histr = cv2.calcHist(imgs_log[-1],[0],None,[256],[0,256])
# show the plotting graph of an image
# plt.plot(histr)
# plt.show()

#%%
rets, imgs_otsu = thresh_Otsu_Bin(imgs_log, +70)
# plt.imshow(np.invert(imgs_otsu[-1]), cmap = 'gray')

#%%
radius = ROIs[0][2]
masks = create_circular_mask(imgs_otsu, radius, ROIs)
masked_imgs = apply_mask(imgs_otsu, masks)

#%%
mask = masks[0]
img_type = imgs_crop[0]

blank = np.zeros([np.shape(img_type)[0],np.shape(img_type)[1] ],dtype=np.uint8)
blank.fill(255)
masked_blank = blank.copy()
masked_blank[~mask] = 0
components = cv2.connectedComponentsWithStats(masked_blank, 8, cv2.CV_32S)
stats = components[2]   
area_blank = stats[1, cv2.CC_STAT_AREA]
num_imgs = np.shape(masked_imgs[0])[0]

#%%
np_area_img = []
num_np_img = []
bg_area_img = []
num_np_bg = []
signal = []
num_bound_np = []
for i in range(num_imgs):
    spot_area = []
    bg_area = []
    spot_num = []
    bg_num = []
    for j in range(n_ROIs):
        area, num =  count_NP(masked_imgs[j][i])
        if j<int(n_spots):
            spot_area.append(area)
            spot_num.append(num)
        else:
            bg_area.append(area)
            bg_num.append(num)
    np_area_img.append(round(np.mean(spot_area),3))   
    bg_area_img.append(round(np.mean(bg_area),3))
    signal.append(round(((np.mean(np_area_img) - np.mean(bg_area_img))/area_blank) * 100,3))
    
    num_np_img.append(round(np.mean(spot_num),3))
    num_np_bg.append(round(np.mean(bg_num),3))
    num_bound_np= np.array(num_np_img) - np.array(num_np_bg)
print(" The pixel ratio in the spots for those frames is : ", signal)
plt.plot(signal)
plt.show()


#%%

def crop_imgs_fixed_test(img_list, circle):
    height, width = img_list[0].shape
    center = circle[0,:2]
    print(center)
    lst = []
    for j,img in enumerate(img_list) : 
        indx1 = center[1]-int(height/3)
        indx2 = center[1]+int(height/3)
        indx3 = center[0]-int(width/4)
        indx4 = center[0]+int(width/4)
        lst.append(img[indx1:indx2,  indx3:indx4 ])
        
    return lst


