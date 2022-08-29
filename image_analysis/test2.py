import os
import sys
import numpy as np
import cv2
from tkinter import filedialog, Tk
import math

np.set_printoptions(threshold=sys.maxsize)

point_matrix = np.array([])
nbr_point = 0
counter = 0
mouse = np.array([])
clone = None
keep = False
start = False


def mousePoints(event, x, y, flags, params):
    global counter
    global mouse
    global keep
    global start

    # Left button mouse click event opencv
    if event == cv2.EVENT_LBUTTONDOWN:
        point_matrix[counter] = x, y
        counter = counter + 1
        keep = True
        start = True

    mouse = np.array([x, y])


def drawAnyShape(img):
    global start
    global counter
    global nbr_point
    global keep
    global mouse
    global point_matrix

    clone = img.copy()
    while counter < nbr_point:
        cv2.imshow("Image", img)
        cv2.setMouseCallback("Image", mousePoints)

        if start == True:
            if keep == True:
                clone = np.copy(img)
                keep = False

            img = np.copy(clone)
            cv2.line(
                img=img,
                pt1=(
                    int(point_matrix[counter - 1, 0]),
                    int(point_matrix[counter - 1, 1]),
                ),
                pt2=(int(mouse[0]), int(mouse[1])),
                color=(0, 0, 255),
                thickness=2,
            )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break


def process():

    global nbr_point
    global point_matrix

    img_path = "/home/gata/Bureau/blur_1.jpeg"
    img_raw = cv2.imread(img_path)
    img_dim = np.shape(img_raw)[:2]

    reduce_factor = 0.15

    reduced_img_raw = cv2.resize(
        img_raw,
        (int(img_dim[1] * reduce_factor), int(img_dim[0] * reduce_factor)),
        interpolation=cv2.INTER_AREA,
    )

    nbr_point = int(input()) + 1
    point_matrix = np.zeros((nbr_point, 2), np.int32)
    drawAnyShape(reduced_img_raw)

    mask = np.zeros_like(reduced_img_raw)
    cv2.fillPoly(mask, pts=[point_matrix], color=(255, 255, 255))
    masked_img = cv2.bitwise_and(reduced_img_raw, mask)
    px_ROI = np.count_nonzero(masked_img != 0) / 3
    px_no_ROI = np.count_nonzero(masked_img == 0) / 3

    print(px_ROI)
    print(px_no_ROI)

    min = np.min(point_matrix, axis=0)
    max = np.max(point_matrix, axis=0)
    reduced_img_raw = reduced_img_raw[min[1] : max[1], min[0] : max[0]]

    cut_off = np.where(masked_img < 150, int(0), int(255)).astype("uint8")

    cv2.imshow("Zoom", cut_off)
    cv2.waitKey(10000)

    px_nanop = np.count_nonzero(cut_off == 0) / 3 - px_no_ROI
    print(px_nanop)
    px_ratio = px_nanop / px_ROI
    print(px_ratio)


if __name__ == "__main__":
    process()
    cv2.destroyAllWindows()
