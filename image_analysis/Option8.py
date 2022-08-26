# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 10:59:44 2022

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
path_blank = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/Blank.png"
brightfield = cv2.imread(path_blank, cv2.IMREAD_GRAYSCALE)
plt.imshow(brightfield, cmap = 'gray')

#%%
imgs_med = temporal_median(imgs, 5)

#%%
path_blank = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/Blank.png"
brightfield = cv2.imread(path_blank, cv2.IMREAD_GRAYSCALE)
plt.imshow(brightfield, cmap = 'gray')

#%%

from cv2_rolling_ball import subtract_background_rolling_ball

option_rollingball = True

# if option_rollingball:
#     smoothed = []
#     for img in imgs_med:
#         #background = restoration.rolling_ball(img)
#         #img_corrected = img-background
#         # 277.076 s
#         #t200_start = process_time() 
img_corrected, background = subtract_background_rolling_ball(imgs[99], 50, light_background=True,
                     use_paraboloid=False, do_presmooth=False)
        #t200_end = process_time() 
        #print(f'Basic Time rolling ball 200 {t200_end-t200_start:.3f}.')
        


#%%
plt.imshow(img_corrected, cmap='gray')
plt.title('after bg cancellation image')
#plt.show()
plt.savefig('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/image_rollball_original.png')
plt.close()

#%%

img_corrected2, background2 = subtract_background_rolling_ball(imgs_med[19], 50, light_background=True,
                     use_paraboloid=False, do_presmooth=False)

plt.imshow(img_corrected2, cmap='gray')
plt.title('after bg cancellation image')
#plt.show()
plt.savefig('C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/image_rollball_tempmed.png')
plt.close()
#%%
def background_corr(img_list, background):
    back_corr = []
    for img in img_list:
        back_corr.append(img/background)
    return back_corr

imgs_rollball = background_corr(imgs_med, background)
#%%

plt.imshow(imgs_rollball[5], cmap = 'gray')

#%%
plt.imshow(img_corrected, cmap = 'gray')
#%%

#imgs_corr = correct_bright(imgs_med, brightfield)
imgs_inv = invert_imgs(imgs_med)

#%%
rets, imgs_bin = binarize_imgs(imgs_inv, 95)

#%%
masks = create_circular_mask(imgs_bin, radius, ROIs)
#%%
masked_imgs = apply_mask(imgs_bin, masks)

#%%
# result = pixel_ratio(masked_imgs, masks, n_spots, n_ROIs)
# slope, R2 = linear_model(result)

#%%
img = imgs_bin[10]
components = cv2.connectedComponentsWithStats(img, 8, cv2.CV_32S)
num_labels = components[0]  # number of labels
labels = components[1]      # label matrix, where each pixel in the same connected component gets the same value
stats = components[2]       # stat matrix
centroids = components[3]   # centroid matrix

i = 5
x = stats[i, cv2.CC_STAT_LEFT]
y = stats[i, cv2.CC_STAT_TOP]
w = stats[i, cv2.CC_STAT_WIDTH]
h = stats[i, cv2.CC_STAT_HEIGHT]
a = stats[i, cv2.CC_STAT_AREA]
(cX, cY) = centroids[i]

output = img.copy()
cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
cv2.circle(output, (int(cX), int(cY)), 4, (0, 0, 255), -1)

componentMask = (labels == i).astype("uint8") * 255
# show our output image and connected component mask
#%%

plt.imshow(labels, cmap = 'gray')

#%%
plt.imshow(imgs_bin[10], cmap = 'gray')

#%%
cv2.imshow("Connected Component", componentMask)
cv2.waitKey(0)
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
            
percent_pixels = nb_pixels / len(img)
print(percent_pixels)

#%%


signal = []
foreground = []
background = []

capture_refresh_time = 2
for img in imgs_bin:
    mes = Measure(NAME_IMG_FOLDER, ROIs, capture_refresh_time)
    result = mes.signal_perImage(img)
    signal = result[0]
    foreground = result[1]
    background = result[2]
    print('final signal', signal)

# Saving result in npy and csv
with open('result.npy', 'wb') as f:
    np.save(f, result)
np.savetxt("result.csv", result)
