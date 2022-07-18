# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 11:51:29 2021
@author: willi+deborah+janet
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.draw import disk
from skimage.draw import circle_perimeter
from logging import getLogger
import cv2



# Path is the path to the results folder
# Capture refresh time is the time between datapoints (after pre-processing)
# Circles is the center (x,y) and radius of the ROIs
# create a new variable tr which is the threshold we want to use after normalizing
class Measure:

    def __init__(self, path, circles, capture_refresh_time):
        self.path = path
        self.circles = circles
        self.capture_refresh_time = capture_refresh_time
        self.log = getLogger('main.Analysis')

    def find_GNP(self, img): 
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
        #print('Number of pixels detected: ', nb_pixels)
        #print('Percentage of pixels detected: ', percent_pixels*100, '%')
        return percent_pixels

    
    def signal_perImage(self, img):

        spot = []
        connectivity = 8 #connectivity for connected components
        for cx, cy, rad in self.circles :
            self.log.info('cx, cy, rad: {},{},{}'.format(cx, cy, rad))
            xvec, yvec = circle_perimeter(cx, cy, rad)  #TODO: change to disk
            #xvec, yvec = disk(cx, cy) #changed by NC as circle function is deprecated
            percent_pixels = self.find_GNP(img[yvec, xvec])  # percentage of pixels detected
            spot.append(percent_pixels)  #Changed

        background = np.sum(np.array(spot[-2:]))/2 #changed to sum
        self.log.info(f'background intensity: {background}')
        foreground = np.sum(np.array(spot[:-2]))/(len(spot)-2) #changed to sum
        self.log.info(f'foreground intensity: {foreground}')
        Signal = foreground - background
        print('Percentage of pixels detected in each ROI (0-1)', spot)
        print('Percentage of pixels corresponding to Background (0-1)', background)
        print('Percentage of pixels corresponding to Foreground (0-1)', foreground)
        print('Percentage of pixels corresponding to Signal', Signal)

        return Signal, foreground, background
    
           
        

# You get the intensity from inside the circles for all the different images
# What does sorted do
 #   def total_intensity(self):
 #       intensity = []
 #       for img_arr in os.listdir(self.path) :
 #           intensity.append(self.signal_perImage(np.load(self.path + img_arr), 70))
 #       return intensity
    
    
# Compute the increase of signal over time
    def compute_slope(self):
        y = self.total_intensity()
        x = (np.array(range(len(y))))*(self.capture_refresh_time)/60
        print(x)
        # We might need to change the fitting function
        reg_lin = np.polyfit(x, y, 1)
        return reg_lin[0]

# This function returns the concentration based on the previously obtained slope and 
    def get_concentration(self, slope):
        slope_calibration = -2446.18395303
        offset = 9.59393346
        concentration = slope*slope_calibration + offset
        if concentration < 0.5:
            return 0.5
        if concentration > 10:
            return 10
        return concentration

    def execute_analysis(self):
        slope = self.compute_slope()
        # print('slope: ',slope)

        concentration = self.get_concentration(slope)
        # print('concentration ',concentration)

        return slope, concentration
