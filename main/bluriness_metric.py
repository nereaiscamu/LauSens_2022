import cv2
import numpy as np
import os


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def blurre_lapace_var(imagePath):
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    return fm


def blurre_JPEG_size_b(imagePath):
    file = open(imagePath)
    file.seek(0, os.SEEK_END)
    file_size_b = file.tell()
    file.close()
    return file_size_b


def downsample_img(imagePath, ratio_scale):
    # ratio_scale: int percentage of downsampling
    image = cv2.imread(imagePath)
    width = int(image.shape[1] * ratio_scale / 100)
    height = int(image.shape[0] * ratio_scale / 100)
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    newImgPath = imgPath[:-4] + "_DS_" + str(ratio_scale) + ".jpeg"
    cv2.imwrite(newImgPath, resized)
    return newImgPath
