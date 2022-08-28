# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 16:27:24 2022

@author: nerea
"""

import imutils
import numpy as np
import cv2
import sys
from numpy.random import default_rng
import numpy.matlib
import os
#import skimage
from skimage import exposure

import matplotlib.pyplot as plt
from skimage.transform import rescale
from skimage.feature import peak_local_max
from skimage.feature import Cascade
from numpy.polynomial import polynomial
from numpy.polynomial.polynomial import polyval2d

import itertools


frame = cv2.imread(ROI_PATH, cv2.IMREAD_GRAYSCALE)
(h, w) = frame.shape[:2]
(cX, cY) = (w // 2, h // 2)
# rotate our image by 45 degrees around the center of the image
M = cv2.getRotationMatrix2D((cX, cY), -45, 1.0)
rotated = cv2.warpAffine(frame, M, (w, h))
cv2.imshow("Rotated by 45 Degrees", rotated)
cv2.destroyAllWindows()
frame2 = imutils.resize(rotated, width=int(0.2 * (np.shape(frame)[1])))


#%%

rots = []
rots.append(rotated)
#%%

# show_frame = cv2.resize(frame,(0,0),fx=0.2, fy=0.2)
# roi = (cv2.selectROI('Select region you want to crop. ', frame, False, False))
roi = np.array(cv2.selectROI('Select region you want to crop. ', frame2, False, False))*5
cv2.destroyAllWindows()
img = rotated[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
plt.imshow(img)

#%%
 # ...resize the image by 0.3
 #...and finally display it
 



#roi = cv2.resize(roi,(0,0),fx=0.25, fy=0.25)

