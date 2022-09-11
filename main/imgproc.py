import os

# path_code = os.path.dirname(__file__)

# important to import file that are not here
# sys.path.append(os.path.abspath(path_code))

import numpy as np
from tkinter import filedialog, Tk
from processing.processing_functions import *
from processing.Functions_2022 import *
from processing.Nc_functions import *
from processing.draw_any_shape import *
import time
from PIL import Image

# from analysis.Select_ROI import execute_roi
# from AcquireAndSave import execute_capture
# from AcquireAndDisplay import execute_focus

name_test = 0
end_process_3 = False
signal = None
num_bound_np = None
slope = None 
concentration = None

def update_every_10(path):
    file_name = os.listdir(path + "\\img_proc\\images")
    
    MED_PATH =  path + "\\img_proc\\images_processed"

    imgs, names = open_images_NC_2(path + "\\img_proc\\images")

    for name in file_name:
        if " " not in name and ".jpeg" in name:
            os.remove(path + "\\img_proc\\images\\" + name)

    name = names[-1]
    #print('Shape imgs', np.shape(imgs))
    #os.chdir(ORIGINAL_FOLDER)
    # 2. Computing median 
    
    imgs_med = temporal_median(imgs, 5)
    print('Saving images in median folder')
    for img in imgs_med:
        im = Image.fromarray(img)
        im.save(os.path.join(MED_PATH, name))


def processing(path, time_to_wait, start = 20):
    print(time_to_wait)
    time.sleep(time_to_wait)
    print("You should STOP live acquisition")

    global signal, num_bound_np, slope, concentration

    
    MED_PATH =  path + "\\img_proc\\images_processed"
    
    print(path + "\\img_proc\\saved_img\\Image_0.png")
    img_path = (path + "\\img_proc\\saved_img\\Image_0.png")  # Path

    imgs_med, _ = open_images_NC_2(MED_PATH)
    
    img_raw_ = cv2.imread(img_path,  cv2.IMREAD_GRAYSCALE)
    print('Shape imgs', np.shape(imgs_med))
    #os.chdir(ORIGINAL_FOLDER)
    # 2. Computing median filter
    #plt.imshow(imgs_crop[4], cmap = 'gray')
    n_spots = 2
    n_bg = 2
    n_ROIs =int(n_spots) + int(n_bg)
    ROIs = Select_ROI_Dynamic_crop_fixR(img_raw_, n_ROIs)
    imgs_inv = invert_imgs(imgs_med)
    # plt.imshow(imgs_log[-1], cmap = 'gray')
    # histr = cv2.calcHist(imgs_log[-1],[0],None,[256],[0,256])
    # show the plotting graph of an image
    # plt.plot(histr)
    # plt.show()
    rets, imgs_otsu = thresh_Otsu_Bin(imgs_inv, 0)
    plt.imshow(np.invert(imgs_otsu[-1]), cmap = 'gray')
    radius = ROIs[0][2]
    masks = create_circular_mask(imgs_otsu, radius, ROIs)
    masked_imgs = apply_mask(imgs_otsu, masks)
    mask = masks[0]
    img_type = imgs_med[0]
    area_blank = np.count_nonzero(mask) #ADD
    num_imgs = np.shape(masked_imgs[0])[0]


    np_area_img = []
    num_np_img = []
    bg_area_img = []
    num_np_bg = []
    signal = []
    num_bound_np = []
    for i in range(num_imgs):
        spot_area = []
        bg_area = []
        spot_num = []
        bg_num = []
        for j in range(n_ROIs):
            area, num =  count_NP(masked_imgs[j][i], 10, 180)
            if j<int(n_spots):
                spot_area.append(area)
                spot_num.append(num)
            else:
                bg_area.append(area)
                bg_num.append(num)
        np_area_img.append(round(np.mean(spot_area),3))   
        bg_area_img.append(round(np.mean(bg_area),3))
        signal.append(round(((np.mean(np_area_img) - np.mean(bg_area_img))/area_blank) * 100,3))
        
        num_np_img.append(round(np.mean(spot_num),3))
        num_np_bg.append(round(np.mean(bg_num),3))
        num_bound_np= np.array(num_np_img) - np.array(num_np_bg)
    
    plt.plot(signal) # Will i york ? TODO
    plt.show()

    slope, R = linear_model(signal, start)
    global name_test
    np.savetxt((path + "\\img_proc\\results\\" + str(name_test) + "_result.csv"), signal)
    np.savetxt((path + "\\img_proc\\results\\" + str(name_test) + "_result_NP.csv"), num_bound_np)
    print("Slope computed")
    concentration_small = get_concentration_small(slope)
    concentration_middle = get_concentration(slope)
    concentration_big = get_concentration_big(slope)
    print("concentration small")
    print(concentration_small)
    print("concentration big")
    print(concentration_big)
    print("concentration middle")
    print(concentration_middle)
    name_test += 1

    global end_process_3
    end_process_3 = True
    return (signal, num_bound_np, slope, concentration_small)