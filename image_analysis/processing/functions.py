import numpy as np
import cv2
from matplotlib import pyplot as plt


BG = 0
BG_V = 0

def test_function():
    print("worked")

def remove_background(img, back_img=0):
    if back_img == 0:
        global BG
        return np.asarray(img)-np.asarray(BG)
    else:
        return np.asarray(img)-np.asarray(back_img)

def create_background(img):
    global BG
    BG = img
    return BG

def create_background_for_video(img1, img2, img3, img4, img5):
    global BG_v
    BG_v = (img1 + img2 + img3 + img4 + img5)/5
    return BG_v

def count_pix(img):
    ret,thresh1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY_INV)
    #plt.hist(thresh1.ravel(),256,[0,256]); plt.show()
    number = np.sum(np.sum(np.array(thresh1)))/255
    return thresh1, number

def removeBackgrounfWithAdaptiveThreshold(img):
    th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
    return th3

def removeBackgrounfWithOtsuThreshold(img):
    ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return th3

def count_pix_alone(img):
    number = np.sum(np.sum(np.array(img)))/255
    return number
