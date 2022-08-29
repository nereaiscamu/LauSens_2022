# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:42:46 2022

@author: nerea
"""

import sys 
import os
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk
from PIL import Image
#from processing.processing_functions import *
from analysis.Analyse_results_with_connected_components import Measure
import cv2
from Nc_functions import *
from sklearn.linear_model import LinearRegression
from skimage import exposure
from test2 import *
import math

np.set_printoptions(threshold=sys.maxsize)

point_matrix = np.array([])
nbr_point = 0
counter = 0
mouse = np.array([])
clone = None
keep = False
start = False




#%%

name_test = 'test_parallel'

#IMG_PATH = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/Images_Lab4/all"
IMG_PATH = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/Images_Lab4/2ngmL_15h_1_part1"
MED_PATH = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/Images_Lab4/Med"
#%%

from PIL import Image


def update_10(IMG_PATH, MED_PATH):
    ## OPENING FILES
    # 1. Loading images in directory folder
    imgs, names = open_images_NC_2(IMG_PATH)
    #print('Shape imgs', np.shape(imgs))
    #os.chdir(ORIGINAL_FOLDER)
    # 2. Computing median filter
    imgs_med = temporal_median(imgs, 5)
    print('Saving images in median folder')
    for i, img in enumerate(imgs_med):
        print(np.shape(img))
        im = Image.fromarray(img)
        im.save(os.path.join(MED_PATH, names[i]))

imgs_med = update_10(IMG_PATH, MED_PATH)


#%%
img_raw = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/Images_Lab4/2ngmL_15h_1_part1/saved_img_078-4timestamp_910.1.jpeg"


#ask gata to give you the path where the image to selec the roi is saved

def processing(MED_PATH, img_raw):
    imgs_med, _ = open_images_NC_2(MED_PATH)
    print('Shape imgs', np.shape(imgs_med))
    #os.chdir(ORIGINAL_FOLDER)
    # 2. Computing median filter
    circle = Select_ROI_Dynamic(img_raw, 1, scale_f = 4 )
    imgs_crop = crop_imgs_fixed(imgs_med, circle)
    #plt.imshow(imgs_crop[4], cmap = 'gray')
    n_spots = input("How many spots are visible? ")
    n_bg = input("How many background regions to use? ")
    n_ROIs =int(n_spots) + int(n_bg)
    img = imgs_crop[-1]
    ROIs = Select_ROI_Dynamic_crop_fixR(img, n_ROIs)
    imgs_inv = invert_imgs(imgs_crop)
    imgs_log = LoG(imgs_inv)
    # plt.imshow(imgs_log[-1], cmap = 'gray')
    # histr = cv2.calcHist(imgs_log[-1],[0],None,[256],[0,256])
    # show the plotting graph of an image
    # plt.plot(histr)
    # plt.show()
    rets, imgs_otsu = thresh_Otsu_Bin(imgs_log, +70)
    plt.imshow(np.invert(imgs_otsu[-1]), cmap = 'gray')
    radius = ROIs[0][2]
    masks = create_circular_mask(imgs_otsu, radius, ROIs)
    masked_imgs = apply_mask(imgs_otsu, masks)
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
    # plt.plot(signal)
    # plt.show()
    slope, R = linear_model(signal, 10)
    np.savetxt((name_test + "_result.csv"), signal)
    concentration = 

    return (signal, num_bound_np, slope)

signal, num_bound_np, slope = processing(MED_PATH, img_raw)