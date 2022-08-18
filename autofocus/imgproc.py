import sys 
import os

#path_code = os.path.dirname(__file__)

#important to import file that are not here
#sys.path.append(os.path.abspath(path_code))

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk
from PIL import Image
from processing_functions import *
from Analyse_results_with_connected_components import Measure
import cv2
from Functions_2022 import *

#from analysis.Select_ROI import execute_roi
#from AcquireAndSave import execute_capture
#from AcquireAndDisplay import execute_focus

def process():
    ## OPENING FILES
    ORIGINAL_FOLDER = os.path.dirname(os.path.realpath(__file__))
    print('THIS IS ORIGINAL FOLDER PATH', str(ORIGINAL_FOLDER))
    IMG_FOLDER = os.path.join('img_proc/images') #Folder where the images taken by the camera to be processed will be located
    IMG_PROCESSED_FOLDER = os.path.abspath('img_proc/images_processed')  #Folder where the resulting images will be located


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

    #%%
    width = height = int(ROIs[0,2]*2.5)
    radius = ROIs[0][2]

    inv_imgs = invert_imgs(imgs)
    smoothed = smooth_background(inv_imgs)
    open_imgs = opening(smoothed, iterations = 1)
    #bin_imgs = thresh_Otsu_Bin(open_imgs)
    masks = create_circular_mask(open_imgs, radius, ROIs)
    masked_imgs = apply_mask(open_imgs, masks)
    result = pixel_ratio(masked_imgs, masks, n_spots, n_ROIs)
    slope, R2 = linear_model(result)
    print(str(slope))
    print("Writing to result.txt")
    f = open("results.txt", "w")
    f.write("Results :")
    f.write("Signal : " + str(result))
    # f.write("Mean sig : " + str(result[1]))
    # f.write("Mean bg : " + str(result[2]))
    f.close()
