# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 11:52:21 2022

@author: nerea
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
from skimage import exposure

# from numpy.random import default_rng
# import numpy.matlib
# import skimage


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
imgs = open_images_NC(IMG_PATH)
print('Shape imgs', np.shape(imgs))
os.chdir(ORIGINAL_FOLDER)

#%%
n_spots = input("How many spots are visible? ")
n_bg = input("How many background regions to use? ")
n_ROIs =int(n_spots) + int(n_bg)
ROIs = Select_ROI_Dynamic(ROI_PATH, n_ROIs, scale_f = 4 )

#%%
width = height = int(ROIs[0,2]*2.5)
radius = ROIs[0][2]


#%%
path_blank = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/Blank.png"
brightfield = cv2.imread(path_blank, cv2.IMREAD_GRAYSCALE)
plt.imshow(brightfield, cmap = 'gray')




corr_list = correct_bright(imgs, brightfield)

inv_imgs = invert_imgs(corr_list)
#%%

smoothed = smooth_background(inv_imgs)
plt.imshow(smoothed[0], cmap = 'gray')
#%%
imgs_eq = equalize(corr_list)
plt.imshow(imgs_eq[0], cmap = 'gray')

#%%
bin_imgs = thresh_Otsu_Bin(imgs_eq)
plt.imshow(bin_imgs[0], cmap = 'gray')
# binary_mask = inv_imgs[0] < 110
# fig, ax = plt.subplots()
# plt.imshow(binary_mask, cmap="gray")
# plt.show()

# bin_imgs = []
# bin_imgs.append(binary_mask)

#%%

open_imgs = opening(bin_imgs, iterations = 1, kernel_size = 3)


op_img = Image.fromarray(bin_imgs[0])    
        
op_img.show()  

#%%
masks = create_circular_mask(open_imgs, radius, ROIs)
#%%
masked_imgs = apply_mask(open_imgs, masks)

#%%
result = pixel_ratio(masked_imgs, masks, n_spots, n_ROIs)
slope, R2 = linear_model(result)

''' HERE WE SHOULD TRY DIFFERENT MODELS TO FIT THE DATA AND THEN WE CAN ALSO KNOW 
AN ESTIMATE OF THE CONCENTRATION 
Also, we can use the connectivity to check the number of NP
Link here: https://stackoverflow.com/questions/35854197/how-to-use-opencvs-connectedcomponentswithstats-in-python'''


# inv_imgs = invert_imgs(imgs)
# bin_imgs = thresh_Otsu_Bin(inv_imgs)

# img_test = bin_imgs[0]
# connectivity = 8  # You need to choose 4 or 8 for connectivity type
# num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img_test , connectivity , cv2.CV_32S)
# nb_pixels = 0
# for c in range(0, num_labels):
#     if c == 0:
#         #print("background")
#         continue
#     else:
#         #print("Signal")
#         area = stats[c, cv2.CC_STAT_AREA]
#         if((area>9) & (area<90)): #TODO: before it was 3, 30
#             nb_pixels = nb_pixels + area 
            
# labels_img = Image.fromarray(labels)    
        
# labels_img.show()             

# percent_pixels = nb_pixels / stats[0, cv2.CC_STAT_AREA]*100

# print(percent_pixels)
# #%%

# histogram, bin_edges = np.histogram(inv_imgs[0], bins=256, range=(0, 1))

# #%%
# t = skimage.filters.threshold_otsu(inv_imgs[0])
# print("Found automatic threshold t = {}.".format(t))



# binary_mask = smoothed[0] < 120

# fig, ax = plt.subplots()
# plt.imshow(binary_mask, cmap="gray")
# plt.show()


# #%%
# plt.figure()
# plt.title("Grayscale Histogram")
# plt.xlabel("grayscale value")
# plt.ylabel("pixel count")
# plt.xlim([0.0, 1.0])  # <- named arguments do not work here

# plt.plot(bin_edges[0:-1], histogram)  # <- or here
# plt.show()


