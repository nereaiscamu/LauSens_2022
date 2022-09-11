import os
import sys
import numpy as np
import cv2
from tkinter import filedialog, Tk
import math

np.set_printoptions(threshold=sys.maxsize)

img_batch = None


def process():

    img_path = "/home/gata/Bureau/blur_1.jpeg"
    img_raw = cv2.imread(img_path)

    img_batch = img_raw

    img_path = "/home/gata/Bureau/blur_2.jpeg"
    img_raw = cv2.imread(img_path)

    img_batch = np.stack((img_batch, img_raw))

    img_path = "/home/gata/Bureau/blur_3.jpeg"
    img_raw = cv2.imread(img_path)

    img_batch = np.concatenate((img_batch, np.array([img_raw])), axis=0)
    print(np.shape(img_batch))

    res = np.median(img_batch, axis=0)

    print(np.shape(res))


if __name__ == "__main__":
    process()
