# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 15:20:54 2021

@author: willi
"""

#### You want this section to show the last image and let you choose 4 circular ROI's in the image
import cv2
import numpy as np


#Still need to change this such that after being deleted the circle actually dissapears
def click_event(event, x, y, flags, params):
   # checking for left mouse clicks, at the moment left mouse clicks are considered as signal 
   [imgc, circles, ROI_radius] = params

   
   if event == cv2.EVENT_LBUTTONDOWN:
        temp = np.copy(imgc)

        circles.append(np.array([x, y, ROI_radius]))
  
        # displaying the coordinates of the new circle
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(temp, str(x) + ',' +
                    str(y), (x,y), font,
                    1, (255, 0, 0), 2)
        print_ROI(temp, circles)
  
   # checking for right mouse clicks  , considered as background   
   if event==cv2.EVENT_RBUTTONDOWN:
       temp = np.copy(imgc)
       del circles[-1]  
       print_ROI(temp, circles)        
        
       
def print_ROI(temp, circles):
    for circle in circles:
        cv2.circle(temp, center=tuple(circle[:2]), radius=circle[2],
                   color=(255,255,0), thickness=2)
    cv2.imshow('image', temp)
    
    
def execute_roi(path_image, image_size, cc):
    print('Select the ROI. Press right button if you want to delete. The last 2 ROIs will be used as background. Press \'q\' when you have finished. ')
    circles = [] 
    ROI_radius = cc
    
    # reading the image
    img = cv2.resize(cv2.imread(path_image, 0), image_size)

    cv2.startWindowThread()
    # displaying the image
    cv2.imshow('image', img)

    #global imgc
    imgc = np.copy(img)
    
    params = [imgc, circles, ROI_radius]
  
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback('image', click_event, params)
  
    # wait for a key to be pressed to exit
    cv2.waitKey(0)
  
    # close the window
    #cv2.waitKey(1)
    cv2.destroyAllWindows()
    #cv2.waitKey(1)
    
    return circles



# if __name__=="__main__":
#     execute_roi(path_image, image_size, 100)
