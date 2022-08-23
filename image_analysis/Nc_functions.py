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
import skimage
from skimage import exposure


#---------------------------------------------------------------------------------------------------------------------------------------

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
        elif key == ord('e'):
             R += 20
        elif key == ord('r'):
             R -= 20
     
        show_frame = frame.copy()
        show_frame = cv2.circle(show_frame,(X,Y),R,(255,255,255),20)
         # ...resize the image by 0.3
        show_frame = cv2.resize(show_frame,(0,0),fx=0.1, fy=0.1)
        
         #...and finally display it
        cv2.imshow("SimpleLive_Python_uEye_OpenCV", show_frame)
         
    cv2.destroyAllWindows()
            
    return [X,Y,R]


def Select_ROI_Dynamic(path_image, n,  scale_f = 4):
    print('Select the ROI. Press right button if you want to delete. The last 2 ROIs will be used as background. Press \'q\' when you have finished. ')
    ROI  = []
    R0 = 100
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


def crop(img_list, ROIs, width, height):
    centers = ROIs[:,:2]
    lst = []
    for i, center in enumerate(centers):
        crop_list = np.zeros([np.shape(img_list)[0], height, width], dtype = np.uint8)
        for j,img in enumerate(img_list) : 
            indx1 = center[0]-int(height/2)
            indx2 = center[0]+int(height/2)
            indx3 = center[1]-int(width/2)
            indx4 = center[1]+int(width/2)
            crop_list[j,:,:] = img[indx3:indx4, indx1:indx2]
        lst.append(list(crop_list))
        
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

def pixel_ratio(img_list, masks, n_spots, n_ROIs):
    
    # 1- Create a blank mask
    
    mask = masks[0]
    img_type = img_list[0][0]
    blank = np.zeros([np.shape(img_type)[0],np.shape(img_type)[1] ],dtype=np.uint8)
    blank.fill(255)
    masked_blank = blank.copy()
    masked_blank[~mask] = 0
    num_white_mask = cv2.countNonZero(masked_blank) 
    
    # 2- Compute mean signal inside each image masked for each ROI
    
    num_imgs = np.shape(img_list[0])[0]
    
    sig_per_img = []
    bg_per_img = []
    signal = []
    for i in range(num_imgs):
        spot_signal_list = []
        bg_signal_list = []
        print(i)
        for j in range(n_ROIs):
            num_white = cv2.countNonZero(img_list[j][i])  
            if j<int(n_spots):
                spot_signal_list.append(num_white)
            else:
                bg_signal_list.append(num_white)
        sig_per_img.append(round(np.mean(spot_signal_list),3))   
        bg_per_img.append(round(np.mean(bg_signal_list),3))
        signal.append(round(((np.mean(spot_signal_list) - np.mean(bg_signal_list))/num_white_mask) * 100,3))
        
    print(" The pixel ratio in the spots for those frames is : ", signal)
        
    return signal

from sklearn.linear_model import LinearRegression


def linear_model(signal):
    model = LinearRegression()
    x = np.arange(0, len(signal)).reshape(-1,1)
    y = np.array(signal)
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

#, (sig_per_img/num_white_mask)*100, (bg_per_img/num_white_mask)*100


# def pixel_ratio(img_list, masks, n_spots):
#     # 1- Create a blank mask
#     mask = masks[0]
#     img_type = img_list[0][0]
#     blank = np.zeros([np.shape(img_type)[0],np.shape(img_type)[1] ],dtype=np.uint8)
#     blank.fill(255)
#     masked_blank = blank.copy()
#     masked_blank[~mask] = 0
#     num_white_mask = cv2.countNonZero(masked_blank) 

    
#     # 2- Compute mean signal inside each image masked for each ROI

#     spot_signal_list = []
#     bg_signal_list = []
#     for i in range(np.shape(img_list)[0]):
#         for j, img in enumerate(img_list[i]):
#             num_white = cv2.countNonZero(img)  
#             if i<int(n_spots):
#                 spot_signal_list.append(num_white)
#             else:
#                 bg_signal_list.append(num_white)
#     mean_sig = np.mean(spot_signal_list)
#     mean_bg = np.mean(bg_signal_list)
    
#     # 3- Final signal is the one on the spots - the background 
#     #(normalized by the maximum signal possible in a circular mask)
#     signal = ((mean_sig - mean_bg)/num_white_mask) * 100
#     print(" The pixel ratio in the spots for those frames is : ", round(signal, 3))
#     return signal, (mean_sig/num_white_mask)*100, (mean_bg/num_white_mask)*100



def thresh_Otsu_Bin(img_list):
    #thresh_list = np.zeros([np.shape(img_list)[0], np.shape(img_list)[1], np.shape(img_list)[2]], dtype = np.uint8)
    thresh_list = []
    for i, img in enumerate(img_list):
        ret, thresh1 = cv2.threshold(img,0,255,cv2.THRESH_OTSU)
        thresh_list.append(thresh1.astype(np.uint8))
    return thresh_list


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


#%%Background smoothing functions (adapted from SensUs 2019, similar to Matlab code of BIOS lab)
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import rescale
from skimage.feature import peak_local_max
from numpy.polynomial import polynomial
from numpy.polynomial.polynomial import polyval2d

import itertools



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

def polyfit2d_alt1(x, y, z, order=3):
    # 3rd order polynomial 
    # https://discuss.dizzycoding.com/python-3d-polynomial-surface-fit-order-dependent/
    ncols = (order + 1)**2
    G = np.zeros((x.size, ncols))
    ij = itertools.product(range(order+1), range(order+1))
    for k, (i,j) in enumerate(ij):
        G[:,k] = x*i * y*j
    m, _, _, _ = np.linalg.lstsq(G, z)
    return m

def smooth_background(imgs, rescale_factor=0.2, poly_deg=[1,1]): #before it was 1,2
    '''
    Function from SensUs 2019
    Smooths the background of the image by modeling the background with a polynomial 
    surface by regression on the local maximum intensity peaks and dividing the original
    image by this surface.
    Parameters
    ----------
    img : list of ndarray images
    rescale_factor : float or int, optional
        The scaling of the image used to fit the polynomial surface. The default is 0.2.
    poly_deg : list or double, optional
        List where the first and secong elements are the polynomial degrees on the x and y axis respectively. The default is [1,2].
    Returns
    -------
    the input image with smoothed background.
    '''
    
    imgs_corrected = []
    for img in imgs:
        img_ = rescale(img, rescale_factor, preserve_range=True)
        BW = peak_local_max(img_, indices=False)
        k = BW*img_
        
        ind = np.nonzero(k)
        print(np.shape(ind))
        z = k[ind]
        
        #Watch out polynomial degree might change depending on background. We chose [1, 2], because deformation looked "cylindrical"
        #   but [2, 2] or other could make sense depending on deformation.
        p = polyfit2d(ind[0],ind[1],z, poly_deg)
        xx, yy = np.meshgrid(np.linspace(rescale_factor, img_.shape[0], img.shape[0]), 
                             np.linspace(rescale_factor, img_.shape[1], img.shape[1]))
        background = np.transpose(polyval2d(xx, yy, p))
        
        img_corrected = img/background
        #img_corrected = img_corrected.astype(np.uint8)
        
        imgs_corrected.append(img_corrected.astype(np.uint8))
    
    return imgs_corrected


def linfit_3D(imgs):
    '''Method for linear fit and background correction from here:
    https://de.mathworks.com/matlabcentral/answers/45680-faster-method-for-polyfit-along-3rd-dimension-of-a-large-3d-matrix#answer_55902
    '''
    newarray = np.dstack(imgs)
    size = np.shape(newarray)
    rng = default_rng(42)
    num = size[2]
    x = rng.random(num)
    z = 1 # first degree polynomial
    V =  np.c_[np.ones((num, 1)), np.cumprod((np.matlib.repmat(x, 1, z).reshape(z,num).T), 1)]
    M = V.dot(np.linalg.pinv(V))
    
    p1 = np.transpose(newarray, (2, 0, 1))
    p1 = p1.reshape(size[2], size[0]*size[1])
    polyCube = M.dot(p1)
    polyCube = np.reshape(polyCube,(size[2], size[0],size[1]));
    polyCube = np.transpose(polyCube,[1, 2, 0]);
    
    imgs_poly = []
    
    for i in np.arange(0,num):
        imgs_poly.append(polyCube[:,:,i].astype(np.uint8))
    return imgs_poly