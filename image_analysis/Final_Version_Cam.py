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

'''name_test = '2ngml_log_15h_1'
name_test_ = name_test+'_nobg' '''

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

name_test = NAME_IMG_FOLDER+'_Otsu' #ADD

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

#imgs_med = temporal_median(imgs, 5)
'''frame = cv2.imread(ROI_PATH, cv2.IMREAD_GRAYSCALE)
roi = cv2.selectROI('Select region you want to crop. ', frame, False, False)

imgs_crop = []
for img in imgs:
    img_crop = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    imgs_crop.append(img_crop)

plt.imshow(img_crop)
plt.show()'''

#%%
#works well at 800
'''circle = Select_ROI_Dynamic(ROI_PATH, 1, scale_f = 4 )
imgs_crop = crop_imgs_fixed(imgs, circle)'''
#plt.imshow(imgs_crop[4], cmap = 'gray')

#%%
n_spots = 2#input("How many spots are visible? ")
n_bg = 2#input("How many background regions to use? ")
n_ROIs =int(n_spots) + int(n_bg)
#img = imgs_crop[-1]
img = imgs[-1]
ROIs = Select_ROI_Dynamic_crop_fixR(img, n_ROIs)

#%%
imgs_inv = invert_imgs(imgs) #imgs_crop
#imgs_log = LoG(imgs_inv)

'''plt.imshow(imgs_inv[6])
plt.show()
plt.imshow(imgs_log[6])
plt.show()'''

# plt.imshow(imgs_log[-1], cmap = 'gray')
# histr = cv2.calcHist(imgs_log[-1],[0],None,[256],[0,256])
# show the plotting graph of an image
# plt.plot(histr)
# plt.show()

#%%
'''
for i in range(20):
    rets, imgs_otsu = thresh_Otsu_Bin(imgs_log, i+20) #70
    # plt.imshow(np.invert(imgs_otsu[-1]), cmap = 'gray')
    
    plt.imshow(imgs_otsu[6])
    plt.show()

    rets_, imgs_otsu_ = thresh_Otsu_Bin(imgs_inv, -i)
    # plt.imshow(np.invert(imgs_otsu[-1]), cmap = 'gray')
    
    plt.imshow(imgs_otsu_[6])
    plt.show()
    
    thresh_list = []
    rets = []
    
    for j, img in enumerate(imgs_inv):
       
        ret_mod = i+100
        ret2, thresh2 = cv2.threshold(img, ret_mod, 255, cv2.THRESH_BINARY)
        thresh_list.append(thresh2.astype(np.uint8))
        rets.append(ret_mod)
        
    plt.imshow(thresh_list[6])
    plt.show()'''
    
#rets_, imgs_otsu = thresh_Otsu_Bin(imgs_log, 70)#-14)

for i in range(1):
    rets_, imgs_otsu = thresh_Otsu_Bin(imgs_inv, i)#-14)
    plt.imshow(imgs_otsu[60])
    plt.title(i)
    plt.show()
    plt.imshow(imgs_otsu[120])
    plt.title(i)
    plt.show()
    
'''for i in range(20):
    thresh_list = []
    rets = []
    
    for j, img in enumerate(imgs_inv):
       
        ret_mod = i+80#110
        ret2, thresh2 = cv2.threshold(img, ret_mod, 255, cv2.THRESH_BINARY)
        thresh_list.append(thresh2.astype(np.uint8))
        rets.append(ret_mod)
        
    plt.imshow(thresh_list[0])
    plt.title(ret_mod)
    plt.show()
    
    plt.imshow(thresh_list[120])
    plt.title(ret_mod)
    plt.show()'''
#%%
radius = ROIs[0][2]
masks = create_circular_mask(imgs_otsu, radius, ROIs)
masked_imgs = apply_mask(imgs_otsu, masks)

#%%
mask = masks[0]
img_type = imgs[0]

'''blank = np.zeros([np.shape(img_type)[0],np.shape(img_type)[1] ],dtype=np.uint8)
blank.fill(255)
masked_blank = blank.copy()
masked_blank[~mask] = 0
components = cv2.connectedComponentsWithStats(masked_blank, 8, cv2.CV_32S)
stats = components[2]   
area_blank = stats[1, cv2.CC_STAT_AREA]
print('Area Nerea:'+str(area_blank))
print(np.count_nonzero(mask))'''

area_blank = np.count_nonzero(mask) #ADD
num_imgs = np.shape(masked_imgs[0])[0]

#%%
#Test different connected components sizes
# TODO fix minn, maxx, plot connectivity
mins = [3, 5, 10]
maxs = [150, 160, 180]
for k in range(1):
    for m in range(1):
        min_ = 10#mins[k]
        max_ = 180#maxs[m]
    
        np_area_img = []
        num_np_img = []
        bg_area_img = []
        num_np_bg = []
        signal = []
        signal_ = []
        num_bound_np = []
        for i in range(num_imgs):
            spot_area = []
            bg_area = []
            spot_num = []
            bg_num = []
            for j in range(n_ROIs):
                area, num =  count_NP(masked_imgs[j][i], minn=min_, maxx=max_)
                if j<int(n_spots):
                    spot_area.append(area)
                    spot_num.append(num)
                else:
                    bg_area.append(area)
                    bg_num.append(num)
            np_area_img.append(np.mean(spot_area))   
            bg_area_img.append(np.mean(bg_area))
            signal.append(((np.mean(np_area_img) - np.mean(bg_area_img))/area_blank) * 100)
            signal_.append(((np.mean(np_area_img))/area_blank) * 100)
            
            num_np_img.append(np.mean(spot_num))
            num_np_bg.append(np.mean(bg_num))
            num_bound_np= np.array(num_np_img) - np.array(num_np_bg)
        print(" The pixel ratio in the spots for those frames is : ", signal)
        plt.plot(signal)
        plt.show()

#%%
'''plt.imshow(masked_imgs[0][159], cmap='gray')
plt.show()

plt.imshow(imgs[159], cmap='gray')
plt.show()'''


#%%
# Saving result in npy and csv

np.savetxt((name_test + "_result.csv"), signal)
np.savetxt((name_test + "_result_NP.csv"), num_bound_np)
#np.savetxt((name_test_ + "_result.csv"), signal_)

#%%

slope, R = linear_model(signal, 10)

#%%
plt.imshow(imgs_otsu[-1], cmap = 'gray')