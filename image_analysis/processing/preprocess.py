#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 11:14:53 2021

@author: janet
"""


import sys 
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from processing.processing_functions import temporal_mean_filter, save_imgs, temporal_median_filter, open_images, binarize_imgs, correct_background, select_ROI, invert_imgs, mask_ROIs
from analysis.Analyse_results_with_connected_components import Measure
from skimage import io
import time
from IPython.display import clear_output


def load_image(filename):
    """
    Function to load an image of format jpg, png, tiff
    :param filename : name of the image to open
    :return img : image as array
    """
    print('\n Opening image '+str(filename)+' ...')

    if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
        time.sleep(0.3)
        img = np.array(Image.open(filename))
        return img
    elif filename.endswith('tiff') or filename.endswith('tif'):
        time.sleep(0.3)
        img = np.array(io.imread(filename))
        return img
    else:
        pass


def select_ROI_image(path):
    """
    Function to select the image to which select ROI
    :param path: path of the directory
    :return:
        path_ROI: path of the image
    """
    os.chdir(path)  #TODO: NOT SURE ABOUT THIS
    print(os.getcwd())
    files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation
    print(files)
    path_ROI = os.path.join(path, files[-1])  # getting the last one
    #print('\n Opening image to select ROI ' + str(filename) + ' ...')

    return path_ROI


def preprocess(imgs, window_size, threshold, ORIGINAL_FOLDER): 
    """
    Runs the preprocessing
    :param imgs:
    :param window_size:
    :param threshold:
    :param ORIGINAL_FOLDER:
    :return:
        imgs_avg
        imgs_thresh
    """
    # 1. Temporal median filter: to remove moving objects
    imgs_avg = temporal_median_filter(imgs, window_size)
    print('Averaged images shape: ', np.shape(imgs_avg))
    #imgs_median = temporal_median_filter(imgs, 5)
    
    # 2. Background illumination intensity correction
    imgs_corrected = correct_background(imgs_avg, ORIGINAL_FOLDER)  #TODO: WARNING IMGS_AVG
    print('Corrected images shape: ', np.shape(imgs_corrected))
    
    # 3. Inverting image (our AU-NP spots will be white ~255)
    imgs_inv = invert_imgs(imgs_corrected)
    print('Inverted images shape: ', np.shape(imgs_inv))
    
    # 4. Binarizing images: we will have a binary image based on a threshold
    rets, imgs_thresh = binarize_imgs(imgs_inv, threshold)   #TODO: FIND THRESHOLD
    print('Thresholded images shape: ', np.shape(imgs_thresh))
    
    return imgs_avg, imgs_thresh



def analysis(img, NAME_IMG_FOLDER, ROIs, framerate):
    """
    Analysis function to run the analysis.
    Signal as percentage of pixels, computed as Signal = Foreground - Background
    :param img:
    :param NAME_IMG_FOLDER:
    :param ROIs:
    :param framerate:
    :return:
    """
    mes = Measure(NAME_IMG_FOLDER, ROIs, framerate)
    result = mes.signal_perImage(img)
    signal = result[0]
    foreground = result[1]
    background = result[2]
    print('final signal', signal)
    
    return result


def live_plot(x, y, figsize=(7,5), title=''):
    #clear_output(wait=True)
    fig = plt.figure(figsize=figsize)
    plt.plot(x, y)
    #plt.title(title)
    fig.clear(True)
    #plt.grid(True)
    #plt.xlabel('epoch')
    #plt.legend(loc='center left') # the plot evolves to the right
    plt.show();

    
    



