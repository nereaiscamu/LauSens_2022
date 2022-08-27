# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 19:30:37 2022

@author: nerea
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.draw import disk
from skimage.draw import circle_perimeter
from logging import getLogger
import cv2



def find_GNP_NC2(img): 
    ''' Function that will compute the connected components and return the number of components
    between 3-5 pixels TO BE DISCUSSED IF PIXELS CHANGE SIZE WITH PREPROCESSING
    Connected components of sizes 1 or 2 and above 30 will be disconsidered.
    
    An AU-NP is considered as a connected component with size between ????? TODO
     
    input:
        img: 1-D array with intensity values at the ROI area
    returns: 
        nb_pixels: number of pixels corresponding to AU-NP
        percent_pixels: percentage of pixels that correspond to a connected component
        labels: label matrix, where each pixel in the same connected component gets the same value
    '''

    components = cv2.connectedComponentsWithStats(img, 8, cv2.CV_32S)
    num_labels = components[0]  # number of labels
    labels = components[1]      # label matrix, where each pixel in the same connected component gets the same value
    stats = components[2]       # stat matrix
    centroids = components[3]   # centroid matrix
    
    nb_pixels = 0
    num_NP = 0
    for c in range(0, num_labels):
        if c == 0:
            #print("background")
            continue
        else:
            #print("Signal")
            area = stats[c, cv2.CC_STAT_AREA]
            if((area>9) & (area<90)): #TODO: before it was 3, 30
                nb_pixels = nb_pixels + area 
                num_NP += 1
    percent_pixels = nb_pixels / len(img)
    #print('Number of pixels detected: ', nb_pixels)
    #print('Percentage of pixels detected: ', percent_pixels*100, '%')
    return percent_pixels, num_NP


#%%






#%%







