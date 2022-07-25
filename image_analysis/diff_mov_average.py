# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 17:40:21 2022

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
from random import randint
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
import numpy.matlib

newarray = np.dstack(imgs)
num = len(newarray[1,1,:])
size = np.size(newarray)


#%%
num = 300
dataCube  = np.random.randint(0, 100, size=(100, 100, 300))

sizeCube = np.size(dataCube)
x = randint(1, num)
z = 3; #maybe for python it should be 2

V = [np.ones(num), np.cumprod(np.matlib.repmat(x, 1, z), 1)];

M = V*np.linalg.pinv(V);


#%%

polyCube = M*reshape(permute(dataCube,[3 1 2]),sizeCube(3),[]);
polyCube = reshape(polyCube,[sizeCube(3) sizeCube(1) sizeCube(2)]);
polyCube = permute(polyCube,[2 3 1]);