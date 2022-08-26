# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 14:29:46 2022

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
inv_imgs = invert_imgs(imgs)

# #%%
# th1 = cv2.adaptiveThreshold(inv_imgs[0],255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
#             cv2.THRESH_BINARY,11,2)
    
# #%%
# #ret,th1 = cv2.threshold(inv_imgs[0],120,255,cv2.THRESH_BINARY)
# th =  []
# th.append(th1)
# open_imgs = opening(th, iterations = 1, kernel_size = 4)
# s = open_imgs[0]
# plt.imshow(s, cmap = 'gray')


# #%%
# bin_imgs = thresh_Otsu_Bin(open_imgs)
# connectivity = 8  # You need to choose 4 or 8 for connectivity type
# num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(s , connectivity , cv2.CV_32S)
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



# #%%
# # # To try the temporal median
# # seq = np.stack(inv_imgs, axis = 2)  #TODO: use last images as well
# # batch = np.median(seq, axis = 2).astype(np.uint8)

# # batch_list = []
# # batch_list.append(batch)

# # # Try to use non-local means
# # #%%
# # a = cv2.fastNlMeansDenoising(batch,	
# #                              h = 3,
# #                              templateWindowSize = 20,
# #                              searchWindowSize = 21)
# # Image.fromarray(a).show()

# # a_l = []
# # a_l.append(a)
#%%
def thresh_Otsu_Bin2(img_list):
    #thresh_list = np.zeros([np.shape(img_list)[0], np.shape(img_list)[1], np.shape(img_list)[2]], dtype = np.uint8)
    thresh_list = []
    ret_list = []
    for i, img in enumerate(img_list):
        ret, thresh1 = cv2.threshold(img,0,255,cv2.THRESH_OTSU)
        thresh_list.append(thresh1.astype(np.uint8))
        ret_list.append(ret)
    return thresh_list, ret_list
       
imgs_log = LoG(inv_imgs)
bin_imgs, thrs = thresh_Otsu_Bin2(imgs_log)

#%%
open_imgs = opening(bin_imgs, iterations = 1, kernel_size = 3)
plt.imshow(open_imgs[0], cmap = 'gray')


#%%

open_imgs = opening(imgs_log, iterations = 2, kernel_size = 5)
bin_imgs, th2 = thresh_Otsu_Bin2(open_imgs)

#%%
masks = create_circular_mask(bin_imgs, radius, ROIs)
masked_imgs = apply_mask(bin_imgs, masks)

#%%
result = pixel_ratio(masked_imgs, masks, n_spots, n_ROIs)
slope, R2 = linear_model(result)


#%%

# find frequency of pixels in range 0-255
histr = cv2.calcHist(open_imgs[0],[0],None,[256],[0,256])

# show the plotting graph of an image
plt.plot(histr)
plt.show()