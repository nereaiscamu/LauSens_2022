# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 16:45:25 2022

@author: nerea
"""


#Libraries
import numpy as np
import cv2
import sys
import time
import functions as fun
from imageio import imread

#---------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------

# Continuous image display
ms_time = time.time()

path = "C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/images_lab3/kohler1.bmp"


def Select_ROI_Dynamic (path):
# displaying the image
    frame = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    
    i = 1
    width = frame.shape[0]
    height = frame.shape[1]
    X = int(width/2)
    Y = int(height/2)
    R = 50
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


ROI = []
BG = []
for i in range(3):
    circle = Select_ROI_Dynamic("C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/LauSens_2022/image_analysis/images_lab3/kohler1.bmp")
    if i == 0:
        ROI.append(circle)
    else:
        BG.append(circle)
        
#%%
        
ROI = np.array(ROI)
BG= np.array(BG)
            
        
frame = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
equal = clahe.apply(frame[:, :])
#bg = clahe.apply(roi_cropped2[:, :])
list1 = []
list2 = []
list1.append(equal)
#list2.append(bg)


#%%

ret, thresh1 = cv2.threshold(equal,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# Remove hair with opening
kernel = np.ones((5,5),np.uint8)
opening = cv2.morphologyEx(thresh1,cv2.MORPH_OPEN,kernel, iterations = 1) #original code had 2 iterations


# ret_gb, thresh_bg = cv2.threshold(roi_cropped2,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# kernel2 = np.ones((6,6),np.uint8)
# # Remove hair with opening
# opening_bg = cv2.morphologyEx(thresh_bg,cv2.MORPH_OPEN,kernel2, iterations = 2) #original code had 2 iterations


list1.append(thresh1)
list1.append(opening)


indx1 = ROI[0][0]-ROI[0][2]
indx2 = ROI[0][0]+ROI[0][2]
indx3 = ROI[0][1]-ROI[0][2]
indx4 = ROI[0][1]+ROI[0][2]

indx1_2 = BG[0][0]-BG[0][2]
indx2_2 = BG[0][0]+BG[0][2]
indx3_2 = BG[0][1]-BG[0][2]
indx4_2 = BG[0][1]+BG[0][2]

spot = opening[indx3:indx4, indx1:indx2]
bg = opening[indx3_2:indx4_2, indx1_2:indx2_2]

list1.append(spot)
list2.append(bg)
#%%
def create_circular_mask(h, w, radius, center=None):
    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])
        
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask

h, w = spot.shape[:2]
mask1 = create_circular_mask(h, w, ROI[0,2])
masked_img = spot.copy()
masked_img[~mask1] = 0

mask2 = create_circular_mask(h, w, BG[0,2])
masked_bg = bg.copy()
masked_bg[~mask2] = 0

list1.append(masked_img)
list2.append(masked_bg)



#%%
num_white = cv2.countNonZero(masked_img)   
num_white_bg = cv2.countNonZero(masked_bg)
blank1 = np.zeros([spot.shape[0],spot.shape[1]],dtype=np.uint8)
blank1.fill(255)
blank1[~mask1] = 0

blank2 = np.zeros([bg.shape[0],bg.shape[1]],dtype=np.uint8)
blank2.fill(255)
blank2[~mask2] = 0
#%%
num_white_mask1 = cv2.countNonZero(blank1) 
num_white_mask2 = cv2.countNonZero(blank2)
 
signal = (num_white /num_white_mask1) - (num_white_bg/ num_white_mask2) *100
signal2 = (num_white)/num_white_mask1 * 100


print('The pixel ratio inside the ROI is ', signal)
print('The pixel ratio inside the ROI without background subtraction is ', signal2)