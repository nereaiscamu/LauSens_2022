# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 14:06:06 2022

@author: nerea
"""
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
from sklearn.linear_model import LinearRegression


import itertools
#---------------------------------------------------------------------------------------------------------------------------------------


def open_images_NC_2(path):

    print('\n Opening images '+str(path)+' ...')
    
    os.chdir(path)  #TODO: NOT SURE ABOUT THIS
    #files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation
    files = sorted(filter(os.path.isfile, os.listdir(path)))  # ordering the images by name
    #imgs = np.zeros((len(files), 3648, 5472))  # list with all the images (jpg or png). TODO: set to size of image
    imgs = []
    filenames = []
    for i, filename in enumerate(files):
        if i<400:
            print('Importing image number '+ str(i) + ' ' + filename)
        #for filename in sorted(os.listdir(path)):
            img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE) #changed by NC to run with other camera images
            imgs.append(img) 
            filenames.append(filename)
    
    return imgs, filenames




def execute_ROI(frame, R):
# displaying the image
    
    i = 1
    width = frame.shape[0]
    height = frame.shape[1]
    X = int(width/2)
    Y = int(height/2)
    print("START")
    while(1):
    # Press q if you want to end the loop
        key = cv2.waitKey(10)
        if key & 0xFF == ord('q'):
            break
        # -------------------------------------------------------------------------------------------------------------------------------------
        # Control panel image 
        if key == ord('t'):
            str = "image%d.jpg"%i
            cv2.imwrite(str,frame)
            i = i+1
            print("taken")
            print(i-1)
        elif key == ord('w'):
             Y -= 50
        elif key == ord('s'):
             Y += 50
        elif key == ord('a'):
             X -= 50
        elif key == ord('d'):
             X += 50
        # elif key == ord('e'):
        #      R += 20
        # elif key == ord('r'):
        #      R -= 20
        show_frame = frame.copy()
        show_frame = cv2.circle(show_frame,(X,Y),R,(255,255,255),20)
         # ...resize the image by 0.3
        show_frame = cv2.resize(show_frame,(0,0),fx=0.1, fy=0.1) #before 0.1, 0.1
        
         #...and finally display it
        cv2.imshow("SimpleLive_Python_uEye_OpenCV", show_frame)
         
    cv2.destroyAllWindows()
            
    return [X,Y,R]


def Select_ROI_Dynamic(path_image, n,  scale_f = 4):
    print('Select the ROI. Press right button if you want to delete. The last 2 ROIs will be used as background. Press \'q\' when you have finished. ')
    ROI  = []
    R0 = 1000
    frame = cv2.imread(path_image, cv2.IMREAD_GRAYSCALE)
    for i in range(n):
        if i == 0:
            circle0 = execute_ROI(frame, R0)
            ROI.append(circle0)  
        else:
            R = circle0[2]
            circle = execute_ROI(frame, R)
            ROI.append(circle) 
    
    return np.array(ROI)


def Select_ROI_Dynamic_crop_fixR(img, n):
    print('Select the ROI. Press right button if you want to delete. The last 2 ROIs will be used as background. Press \'q\' when you have finished. ')
    ROI  = []
    R0 = 400
    frame = img
    for i in range(n):
            circle0 = execute_ROI(frame, R0)
            ROI.append(circle0) 
    
    return np.array(ROI)

def crop_imgs_fixed(img_list, circle):
    height, width = img_list[0].shape
    center = circle[0,:2]
    print(center)
    lst = []
    for j,img in enumerate(img_list) : 
        indx1 = center[1]-int(height/2.5)
        indx2 = center[1]+int(height/2.5)
        indx3 = center[0]-int(width/3)
        indx4 = center[0]+int(width/3)
        # indx1 = center[1]-1500
        # indx2 = center[1]+1500
        # indx3 = center[0]-1000
        # indx4 = center[0]+1000
        lst.append(img[indx1:indx2,  indx3:indx4 ])
        
    return lst



def create_circular_mask(img_list, radius, ROIs):
    centers = ROIs[:,:2]
    img = img_list[0]
    h, w = img.shape[:2]
    mask_list = []
    for i, center in enumerate(centers):
        if center is None: # use the middle of the image
            center = (int(w/2), int(h/2))
        if radius is None: # use the smallest distance between the center and image walls
            radius = min(center[0], center[1], w-center[0], h-center[1])
            
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    
        mask = dist_from_center <= radius
        
        mask_list.append(mask)
        
    return mask_list





def apply_mask(img_list, masks):
    lst = []
    for i, mask in enumerate(masks):
        #masked_imgs = np.zeros([np.shape(img_list)[0], np.shape(img_list)[1], np.shape(img_list)[2]], dtype = np.uint8)
        masked_imgs = []
        for j,img in enumerate(img_list):
            masked_img = img.copy()
            masked_img[~mask] = 0
            masked_imgs.append(masked_img.astype(np.uint8))
        lst.append(masked_imgs)
    return lst

def count_NP(img, minn=9, maxx=90): 
    ''' Function that will compute the connected components and return the number of components
    between 9-90 pixels 
    
    An AU-NP is considered as a connected component with size between 9-90
     
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
    mask = np.zeros(img.shape, dtype="uint8")
    for c in range(0, num_labels):
        if c == 0:
            #print("background")
            continue
        else:
            #print("Signal")
            area = stats[c, cv2.CC_STAT_AREA]
            if((area>minn) & (area<maxx)): #TODO: before it was 3, 30
                nb_pixels = nb_pixels + area 
                num_NP += 1
                
                #componentMask = (labels == c).astype("uint8") * 255
                #mask = cv2.bitwise_or(mask, componentMask)
                
    '''plt.imshow(mask, cmap='gray')
    plt.title('min:'+str(minn)+', max:'+str(maxx))
    plt.show()'''
    #print('Number of pixels detected: ', nb_pixels)
    #print('Percentage of pixels detected: ', percent_pixels*100, '%')
    return nb_pixels, num_NP


def linear_model(signal, start):
    model = LinearRegression()
    x = np.arange(0, len(signal[start:])).reshape(-1,1)
    y = np.array(signal[start:])
    model.fit(x, y)
    r_sq = model.score(x, y)
    print(f"slope: {model.coef_}")
    print(f"intercept: {model.intercept_}")
    print(f"coefficient of determination: {r_sq}")
    plt.plot(x,y)
    plt.show()
    return(model.coef_, r_sq)

def equalize(img_list):
    imgs_eq = []
    for i, img in enumerate(img_list):
        imgs_eq.append((exposure.equalize_hist(img)*255).astype(np.uint8))
    return imgs_eq


def temporal_median(img_list, size_kernel_):
    """ 
    Performs temporal median filter without overlapping.
    Warning: if the number of images is not a multiple of the kernel size, the last images will be lost.
    
    imgs: list of images to process
    size_kernel: number of frames over which computes median filter
    
    """
    print('\n Computing temporal median filter with kernel size ', size_kernel_, '...')
    imgs_med = []
   
    size_kernel = size_kernel_-1
    for i in np.arange(0, len(img_list)//size_kernel) :  
        try:
            seq = np.stack(img_list[i*(size_kernel+1):(size_kernel*(i+1)+i)], axis = 2)  #TODO: use last images as well
            batch = np.median(seq, axis = 2).astype(np.uint8)
            imgs_med.append(batch)
        except:
            print('Could not compute window with indices '+str(i*(size_kernel+1))+' to '+ str((size_kernel*(i+1)+i)))
            
    return imgs_med

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


def thresh_Otsu_Bin(img_list, val):
    #thresh_list = np.zeros([np.shape(img_list)[0], np.shape(img_list)[1], np.shape(img_list)[2]], dtype = np.uint8)
    thresh_list = []
    rets = []
    for i, img in enumerate(img_list):
        ret, thresh1 = cv2.threshold(img,0,255,cv2.THRESH_OTSU)
        ret_mod = ret + val
        ret2, thresh2 = cv2.threshold(img, ret_mod, 255, cv2.THRESH_BINARY)
        thresh_list.append(thresh2.astype(np.uint8))
        rets.append(ret_mod)
    return rets, thresh_list


def LoG(img_list):
    ddepth = cv2.CV_16S
    kernel_size = 5
    log_list = []
    for i, img in enumerate(img_list):
        print(np.shape(img))
        # Remove noise by blurring with a Gaussian filter
        src_gray = cv2.GaussianBlur(img, (3, 3), 0)
        dst = cv2.Laplacian(src_gray, ddepth, ksize=kernel_size)
        abs_dst = cv2.convertScaleAbs(dst)
        log_list.append(abs_dst)
        
    return log_list

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
        
def opening(img_list, iterations = 1, kernel_size = 5):
    kernel = np.ones((kernel_size,kernel_size),np.uint8)
    open_list = []
    
    for i, img in enumerate(img_list):
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations) #original code had 2 iterations
        open_list.append(opening.astype(np.uint8))
        
    return open_list


def get_concentration_small(slope):
    
    slope_calibration = 71673.85798407  #497602.72843897 # before it was 
    offset = 86.41508218 #299.54307958  #before it was 210.26536709
    concentration = slope*slope_calibration + offset
    # if concentration < 0.5:
    #     return 0.5
    # if concentration > 10:
    #     return 10
    return concentration

def get_concentration_big(slope):
    
    slope_calibration = 405400.76981954  #497602.72843897 # before it was 79091.15385922
    offset = 478.19772882 #299.54307958  #before it was 210.26536709
    concentration = slope*slope_calibration + offset
    # if concentration < 0.5:
    #     return 0.5
    # if concentration > 10:
    #     return 10
    return concentration

def get_concentration(slope):
    slope_calibration = 250000  #497602.72843897 # before it was 79091.15385922
    offset = 350 #299.54307958  #before it was 210.26536709
    concentration = slope*slope_calibration + offset
    # if concentration < 0.5:
    #     return 0.5
    # if concentration > 10:
    #     return 10
    return concentration