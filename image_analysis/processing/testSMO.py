# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 16:25:34 2022

@author: nerea
"""
import os
import cv2
from smo import SMO
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

path = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/Images_Lab4/Plasma_2408/saved_img_2.png"
img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

smo = SMO(sigma=0, size=15, shape=(1024, 1024))
background_corrected_image = smo.bg_corrected(img)
#%%
plt.imshow(background_corrected_image, cmap = 'gray')
#%%
plt.imshow(img, cmap = 'gray')

#%%
masked_image = np.ma.masked_greater_equal(img, 255)  # image is uint8 (0-255)

m = plt.imshow(smo.smo_probability(masked_image), vmin=0, vmax=1)
plt.colorbar(m, label="SMO probability")


#%%
plt.imshow(smo.smo_image(masked_image), vmin=0, vmax=1)

#%%

plt.imshow(img, cmap = 'gray')