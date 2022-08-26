# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 15:38:48 2022

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
n_spots = input("How many spots are visible? ")
n_bg = input("How many background regions to use? ")
n_ROIs =int(n_spots) + int(n_bg)
ROIs = Select_ROI_Dynamic(ROI_PATH, n_ROIs, scale_f = 4 )
width = height = int(ROIs[0,2]*2.5)
radius = ROIs[0][2]
#%%
# path_blank = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/Blank.png"
# brightfield = cv2.imread(path_blank, cv2.IMREAD_GRAYSCALE)
# plt.imshow(brightfield, cmap = 'gray')

#%%
imgs_med = temporal_median(imgs, 5)
# Importing OpenCV
import cv2

# Getting the kernel to be used in Top-Hat
filterSize =(3, 3)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,
								filterSize)

# Reading the image named 'input.jpg'
input_image = imgs_med[4]

#%%

# Applying the Top-Hat operation
tophat_img = cv2.morphologyEx(imgs_inv[4],
							cv2.MORPH_TOPHAT,
							kernel)

plt.imshow(tophat_img, cmap = 'gray')

#%%

eq = (exposure.equalize_hist(tophat_img)*255).astype(np.uint8)
plt.imshow(eq, cmap = 'gray')

histr = cv2.calcHist(eq,[0],None,[256],[0,256])
#%%
# show the plotting graph of an image
plt.plot(histr)
plt.show()

#%%
filterSize =(5, 5)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,
								filterSize)
imgs_inv = invert_imgs(imgs_med)

blackhat_img = cv2.morphologyEx(imgs_inv[19], 
                              cv2.MORPH_BLACKHAT,
                              kernel)
eq2 = (exposure.equalize_hist(np.invert(blackhat_img))*255).astype(np.uint8)

plt.imshow(eq2, cmap = 'gray')

#%%
plt.imshow(imgs_med[19], cmap = 'gray')
