# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 17:31:18 2021

@author: Janet
"""

import os
from PIL import Image
import numpy as np
import cv2
from processing.Select_ROI import execute_roi
from skimage.draw import disk
from skimage.draw import circle_perimeter
from skimage import io

#    

def open_images(path):
    """
    Loading images
    
    It also gets the time of creation of the files in order to compute the frame rate afterwards. 
    CAREFUL! Sometimes this might change if you move the file to another folder or computer.
    
    input:
        path: directory where the files are located
    output:
        imgs: list of images
        time_creation: list of dates of creation of the files
    """
    

    time_creation = [] # list with the time of creation of each image
    #parent = os.getcwd()
    #path = os.path.join(parent, PATH)
    print('\n Opening images '+str(path)+' ...')
    
    os.chdir(path)  #TODO: NOT SURE ABOUT THIS
    files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation

    #imgs = np.zeros((len(files), 3648, 5472))  # list with all the images (jpg or png). TODO: set to size of image
    imgs = []

    for i, filename in enumerate(files):
    #for filename in sorted(os.listdir(path)):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg') :
            img_path = os.path.join(path, filename)
            time_creation.append(os.stat(filename).st_ctime)
            #print(img_path)
            #imgs[i,:,:] = np.array(Image.open(img_path))
            img = np.array(Image.open(img_path))[:,:,1] #changed by NC to run with other camera images
            imgs.append(img) #appending the image to the list

        elif filename.endswith('tiff') or filename.endswith('tif') or filename.endswith('.bmp'):
            #imgs[i,:,:] = np.array(io.imread(filename))
            img = np.array(io.imread(filename))[:,:,1] #changed by NC to work with other camera images
            imgs.append(img)
            
        else:
            continue
        
    return imgs, time_creation

def open_images_NC(path):

    print('\n Opening images '+str(path)+' ...')
    
    os.chdir(path)  #TODO: NOT SURE ABOUT THIS
    #files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation
    files = sorted(filter(os.path.isfile, os.listdir(path)))  # ordering the images by name
    #imgs = np.zeros((len(files), 3648, 5472))  # list with all the images (jpg or png). TODO: set to size of image
    imgs = []

    for i, filename in enumerate(files):
        if i<300:
            print('Importing image number '+ str(i) + ' ' + filename)
        #for filename in sorted(os.listdir(path)):
            img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE) #changed by NC to run with other camera images
            imgs.append(img) 
    
    return imgs

#files.sort(key=os.path.getctime)

def select_ROI(ROI_PATH, scale_f = 4, RADIUS = 300):
    """
    Function to select ROIs
    input:
        ROI_PATH: path where the image to which select the ROI is placed
        radius: radius of the ROI
        scale_f: scaling, adapt to laptop (to see full screen)
    output:
        ROIs: array with x, y, radius of size (num_ROIs, 3)
        """
        
    #image_size = (int(5472/scale_f), int(3648/scale_f))
    image_size = (int(4104/scale_f), int(3006/scale_f))
    small_ROIs = execute_roi(ROI_PATH, image_size, int(RADIUS/scale_f))  # returned as x, y, radius
    ROIs = np.array(small_ROIs)*scale_f  # x, y, radius
    print('ROIs:\n', ROIs)
    
    return ROIs

def select_ROI_NC(ROI_PATH, val1, val2, RADIUS, scale_f = 4):
    """
    Function to select ROIs
    input:
        ROI_PATH: path where the image to which select the ROI is placed
        radius: radius of the ROI
        scale_f: scaling, adapt to laptop (to see full screen)
    output:
        ROIs: array with x, y, radius of size (num_ROIs, 3)
        """
        
    #image_size = (int(1379/scale_f), int(1011/scale_f))
    image_size = (int(val1/scale_f), int(val2/scale_f))
    small_ROIs = execute_roi(ROI_PATH, image_size, int(RADIUS/scale_f))  # returned as x, y, radius
    ROIs = np.array(small_ROIs)*scale_f  # x, y, radius
    print('ROIs:\n', ROIs)
    
    return ROIs


def temporal_median_filter(imgs, size_kernel_):
    """ Temporal median filter
    
    Performs temporal median filter without overlapping.
    Warning: if the number of images is not a multiple of the kernel size, the last images will be lost.
    
    imgs: list of images to process
    size_kernel: number of frames over which computes median filter
    
    """
    print('\n Computing temporal median filter with kernel size ', size_kernel_, '...')
    imgs_med = []
   
    size_kernel = size_kernel_-1
    for i in np.arange(0, len(imgs)//size_kernel) :  
        try:
            seq = np.stack(imgs[i*(size_kernel+1):(size_kernel*(i+1)+i)], axis = 2)  #TODO: use last images as well
            batch = np.median(seq, axis = 2).astype(np.uint8)
            imgs_med.append(batch)
        except:
            print('Could not compute window with indices '+str(i*(size_kernel+1))+' to '+ str((size_kernel*(i+1)+i)))
            
    return imgs_med


def temporal_mean_filter(imgs, size_kernel_):
    """ Temporal mean filter
    
    Performs temporal average filter without overlapping
    
    imgs: list of images to process
    size_kernel: number of frames over which computes median filter
    
    """
    print('\n Computing temporal average filter with kernel size ', size_kernel_, '...')
    imgs_med = []
    
    size_kernel = size_kernel_-1
    for i in np.arange(0, len(imgs)//size_kernel) :
        #print('Computing window from '+str(i*(size_kernel+1))+' to '+ str((size_kernel*(i+1)+i)))
        try: 
            seq = np.stack(imgs[i*(size_kernel+1):(size_kernel*(i+1)+i)], axis = 2)  #TODO: use last images as well
            batch = np.mean(seq, axis = 2).astype(np.uint8)
            imgs_med.append(batch)
        except:
            continue
            #print('Number of images = '+str(len(imgs)))
            #print('Could not compute window with indices '+str(i*(size_kernel+1))+' to '+ str((size_kernel*(i+1)+i)))
    
    return imgs_med



def correct_background(imgs, path):
    '''
    Function to correct the background illumination using
    Corrected_Image = (Specimen - Darkfield) / (Brightfield - Darkfield) * 255
    Needs Darkfield.png and Brightfield.png images saved at the main folder
    input:
        imgs: list of BW images as array
    output:
        imgs_corrected
    '''
    
    imgs_corrected = []
    #TODO: THIS WAY IS NOT THE BEST TO GET THE WORKING DIRECTORY, SOMETIMES IT DOES NOT WORK
    #path = os.path.dirname(os.path.realpath('processing_functions.py'))  # Working directory needs to be in main folder SensUs_Code_2021
    os.chdir(path)
    #darkfield = np.array(Image.open(os.path.join("Darkfield.png")))
    #brightfield = np.array(Image.open(os.path.join("Brightfield.png")))
    darkfield = np.array(io.imread(os.path.join("Darkfield.tiff")))
    brightfield = np.array(io.imread(os.path.join("Brightfield.tiff")))


    print('Correcting background illumination intensity...')
    for img in imgs:
        specimen = img
        img_corrected = (specimen - darkfield) / (brightfield - darkfield) * 255
        #Normalizing the result
        img_corrected_norm = np.array((img_corrected-img_corrected.min()) / (img_corrected.max()-img_corrected.min()) * 255, dtype=np.uint8)
        #img_corrected_norm.astype(np.uint8)
        imgs_corrected.append(img_corrected_norm)
    
    #np.array(cv2.normalize(img_corrected, None, alpha=0, beta=255), dtype='int') 
    
    return imgs_corrected


def binarize_imgs(imgs, tr):
    '''
    Binarize images
    Function to binarize a list of images using a threshold.
    input:
        imgs: list of images as arrays
    output:
        rets: array of thresholds
        imgs_thresh: binarized images with a threshold
    '''
    
    print('Binarizing images...')
    rets = []
    imgs_thresh = []
    for image in imgs:
        ret, img_thresh = cv2.threshold(image, tr, 255, cv2.THRESH_BINARY)
        imgs_thresh.append(img_thresh)
        rets.append(ret)
    return rets, imgs_thresh



def invert_imgs(imgs):
    '''
    Invert images
    Function to invert a lsit of images using a threshold.
    input:
        imgs: list of images as arrays
    output:
        imgs_inv: inverted images
    '''
    
    imgs_inv = []
    print('Inverting images...')
    for img in imgs:
        imgs_inv.append(np.invert(img))
    
    return imgs_inv


def mask_ROIs(imgs, ROIs):
    '''
    Function that applies a mask to the image using the ROIs
    input:
        imgs: list of original images (BW)
        ROIs: array with x, y, radius with size (number_ROIs, 3)
    output:
        imgs_masked: masked images (with black background)
    '''
    print('Masking images...')
    xvecs = []
    yvecs = []
    imgs_masked = []
    mask = np.zeros(imgs[0].shape)
    
    for cx, cy, rad in ROIs :
        #self.log.info('cx, cy, rad: {},{},{}'.format(cx, cy, rad))
        xvec, yvec = circle_perimeter(cx,cy,rad) #deprecated
        #xvec, yvec = disk(cx, cy) #changed by NC to implement the disk function which only takes 2 arguments
        xvecs.append(xvec)
        yvecs.append(yvec)
    
    mask[yvecs, xvecs] = True
    
    for img in imgs:
        imgs_masked.append(img*mask)
        
    return imgs_masked



def save_imgs(imgs, path, name):
    print('Saving images in '+str(path)+'...')
    
    #Create the folder
    dir = path
    if not os.path.exists(dir):
        os.mkdir(dir)
    
    for i in np.arange(0, len(imgs)):
        Image.fromarray(imgs[i]).save(os.path.join(path, name+str(i)+'.png'))
        



#%%Background smoothing functions (from SensUs 2019)
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import rescale
from skimage.feature import peak_local_max
from numpy.polynomial import polynomial
from numpy.polynomial.polynomial import polyval2d



def polyfit2d(x, y, f, deg):   #TODO: TRY THIS POLY TO IMAGE WITH ONLY LIGHT
    '''
    Function from SensUs 2019
    Fits a 2d polynomial of degree deg to the points f where f is the value of point [x,y]
    '''
    x = np.asarray(x)
    y = np.asarray(y)
    f = np.asarray(f)
    deg = np.asarray(deg)
    vander = polynomial.polyvander2d(x, y, deg)
    vander = vander.reshape((-1, vander.shape[-1]))
    f = f.reshape((vander.shape[0],))
    c = np.linalg.lstsq(vander, f, rcond=None)[0]
    return c.reshape(deg+1)


def smooth_background(img, rescale_factor=0.1, poly_deg=[2,2]):
    '''
    Function from SensUs 2019
    Smooths the background of the image by modeling the background with a polynomial 
    surface by regression on the local maximum intensity peaks and dividing the original
    image by this surface.
    Parameters
    ----------
    img : ndarray
        Image.
    rescale_factor : float or int, optional
        The scaling of the image used to fit the polynomial surface. The default is 0.1.
    poly_deg : list or double, optional
        List where the first and secong elements are the polynomial degrees on the x and y axis respectively. The default is [1,2].
    Returns
    -------
    the input image with smoothed background.
    '''

    imgs = rescale(img, rescale_factor, preserve_range=True)
    BW = peak_local_max(imgs, indices=False)
    k = BW*imgs
    
    ind = np.nonzero(k)
    z = k[ind]
    
#TODO watch out polynomial degree might change depending on background. We chose [1, 2], because deformation looked "cylindrical"
#   but [2, 2] or other could make sense depending on deformation.
    p = polyfit2d(ind[0],ind[1],z, poly_deg)
    xx, yy = np.meshgrid(np.linspace(0, imgs.shape[0], img.shape[0]), 
                         np.linspace(0, imgs.shape[1], img.shape[1]))

    background = np.transpose(polyval2d(xx, yy, p))
    return background