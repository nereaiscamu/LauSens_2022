# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 17:48:11 2022

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

circle = Select_ROI_Dynamic(ROI_PATH, 1, scale_f = 4 )

#%%
#works well at 800
imgs_crop = crop_imgs(imgs, circle)

#%%
img = imgs_crop[-1]
ROIs = Select_ROI_Dynamic_crop(img, n_ROIs)


#%%
imgs_med = temporal_median(imgs_crop, 5)
#%%
imgs_inv = invert_imgs(imgs_med)

#smoothed = smooth_background(imgs_inv, [1,1])
#plt.imshow(smoothed[-1], cmap = 'gray')

#%%
imgs_log = LoG(imgs_inv)
plt.imshow(imgs_log[-1], cmap = 'gray')

#%%
histr = cv2.calcHist(imgs_log[-1],[0],None,[256],[0,256])
# show the plotting graph of an image
plt.plot(histr)
plt.show()

#%%

rets, imgs_otsu = thresh_Otsu_Bin(imgs_log, +150)

plt.imshow(np.invert(imgs_otsu[-1]), cmap = 'gray')

#%%

masks = create_circular_mask(imgs_otsu, radius, ROIs)
masked_imgs = apply_mask(imgs_otsu, masks)

#%%
result = pixel_ratio(masked_imgs, masks, n_spots, n_ROIs)
slope, R2 = linear_model(result)


# #%%
# img = cv2.imread('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/Images_Lab4\Plasma_2408_2/images_0/saved_img_59-4.jpeg')
# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# plt.imshow(hsv)
# histr = cv2.calcHist(imgs_log[-1],[0],None,[256],[0,256])
# # show the plotting graph of an image
# plt.plot(histr)
# plt.show()
# rets, imgs_bin = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
# plt.imshow(imgs_bin)
#%%






#%%
signal = []
foreground = []
background = []
NP = []
capture_refresh_time = 2
for img in imgs_otsu:
    mes = Measure(NAME_IMG_FOLDER, ROIs, capture_refresh_time)
    result = mes.signal_perImage_NC(img)
    signal.append(result[0])
    foreground.append(result[1])
    background.append(result[2])
    NP.append(result[3])
    
    print('final signal', signal, 
          'Num NP', NP)
    
#%%

slope, R2 = linear_model(signal)
slope2, R22 = linear_model(NP)
#%%

connectivity = 8  # You need to choose 4 or 8 for connectivity type
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats( imgs_otsu[-1], connectivity , cv2.CV_32S)


#%%
output = np.zeros(imgs_otsu[-1].shape, dtype="uint8")
num_NP = 0
for i in range(0, num_labels-1):
    area = stats[i, cv2.CC_STAT_AREA] 
    
    if (area > 9) and (area < 90):
        print('yey')
        # Labels stores all the IDs of the components on the each pixel
        # It has the same dimension as the threshold
        # So we'll check the component
        # then convert it to 255 value to mark it white
        componentMask = (labels == i).astype("uint8") * 255
        num_NP += 1
        # Creating the Final output mask
        output = cv2.bitwise_or(output, componentMask)
        
plt.imshow(np.invert(output), cmap = 'gray')   
print(num_NP)     
#%%

plt.imshow(np.invert(output), cmap = 'gray')
plt.title('NP_3_to_30')
#plt.show()
plt.savefig('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/NP_3_to_30.png')
plt.close()


#%%

plt.imshow(np.invert(labels), cmap = 'gray')
plt.title('All_Labels')
#plt.show()
plt.savefig('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/All_Labels.png')
plt.close()

#%%
a = np.array(np.where(stats[:,4]>15)).T

#%%
b = np.array(np.where(a >100)).T[:,0]

#%%
for i in range(len(b)):
    componentMask = (labels == b[i]).astype("uint8") * 255
    output = cv2.bitwise_or(output, componentMask)
plt.imshow(output, cmap = 'gray')   
#%%
stats = stats[np.where(stats[:,4] > 5)]
for i in range(1, len(stats)):
    componentMask = (labels == i).astype("uint8") * 255

#%%
nb_pixels = 0
for c in range(0, num_labels):
    if c == 0:
        #print("background")
        continue
    else:
        #print("Signal")
        area = stats[c, cv2.CC_STAT_AREA]
        if((area>9) & (area<90)): #TODO: before it was 3, 30
            nb_pixels = nb_pixels + area 