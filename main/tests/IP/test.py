import os
import sys
import numpy as np
import cv2
from tkinter import filedialog, Tk
import math

np.set_printoptions(threshold=sys.maxsize)

point_matrix = np.zeros((3, 2), np.int)
counter = 0
mouse = np.array([])
clone = None
keep_radius = False


def mousePoints(event, x, y, flags, params):
    global counter
    global mouse
    global keep_radius

    # Left button mouse click event opencv
    if event == cv2.EVENT_LBUTTONDOWN:
        point_matrix[counter] = x, y
        counter = counter + 1

        if counter == 2:
            keep_radius = True

    mouse = np.array([x, y])


def selectROI_circle(img):
    global keep_radius

    clone = img.copy()
    while True:
        cv2.imshow("Image", img)
        cv2.setMouseCallback("Image", mousePoints)

        if counter == 1 and not np.array_equal(mouse, point_matrix[0]):
            img = np.copy(clone)
            cv2.line(
                img=img,
                pt1=(int(point_matrix[0, 0]), int(point_matrix[0, 1])),
                pt2=(int(mouse[0]), int(mouse[1])),
                color=(0, 0, 255),
                thickness=2,
            )

        if counter == 2 and not np.array_equal(mouse, point_matrix[1]):
            if keep_radius == True:
                clone = np.copy(img)
                keep_radius = False

            img = np.copy(clone)

            axeLen = int(np.linalg.norm(point_matrix[0] - point_matrix[1]))

            angle = -(
                math.atan2(
                    (point_matrix[0, 1] - point_matrix[1, 1]),
                    -(point_matrix[0, 0] - point_matrix[1, 0]),
                )
                * 180
                / math.pi
            )
            if angle > 0:
                angle += 360

            angle2 = -(
                math.atan2(
                    (point_matrix[0, 1] - mouse[1]),
                    -(point_matrix[0, 0] - mouse[0]),
                )
                * 180
                / math.pi
            )

            cv2.ellipse(
                img,
                (int(point_matrix[0, 0]), int(point_matrix[0, 1])),
                (axeLen, axeLen),
                angle,
                0,
                angle2 - angle,
                (0, 0, 255),
                2,
            )
            cv2.line(
                img=img,
                pt1=(int(point_matrix[0, 0]), int(point_matrix[0, 1])),
                pt2=(int(mouse[0]), int(mouse[1])),
                color=(0, 0, 255),
                thickness=2,
            )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break


def keep_ROI_circle(img):
    print(point_matrix)
    min = np.min(point_matrix, axis=0)
    max = np.max(point_matrix, axis=0)
    print(min)
    print(max)
    print(np.shape(img))

    img = img[min[1] : max[1], min[0] : max[0]]

    cv2.imshow("Zoom", img)
    cv2.waitKey(10000)


def process():

    img_path = "/home/gata/Bureau/blur_1.jpeg"
    img_raw = cv2.imread(img_path)
    img_dim = np.shape(img_raw)[:2]

    reduce_factor = 0.15

    reduced_img_raw = cv2.resize(
        img_raw,
        (int(img_dim[1] * reduce_factor), int(img_dim[0] * reduce_factor)),
        interpolation=cv2.INTER_AREA,
    )

    selectROI_circle(reduced_img_raw)

    keep_ROI_circle(reduced_img_raw)

    raise Exception()

    roi = cv2.selectROI(reduced_img_raw, fromCenter=True)
    img_raw_zoom = img_raw[
        int(roi[1] * 1 / reduce_factor) : int((roi[1] + roi[3]) * 1 / reduce_factor),
        int(roi[0] * 1 / reduce_factor) : int((roi[0] + roi[2]) * 1 / reduce_factor),
        :,
    ]

    reduced_img_raw_zoom = reduced_img_raw[
        int(roi[1]) : int(roi[1] + roi[3]),
        int(roi[0]) : int(roi[0] + roi[2]),
        :,
    ]

    cv2.imshow("Zoom", reduced_img_raw_zoom)
    cv2.waitKey(1000)

    print(np.shape(reduced_img_raw_zoom))
    print(reduced_img_raw_zoom.dtype)
    cut_off = np.where(reduced_img_raw_zoom < 150, int(0), int(255)).astype("uint8")

    print(np.shape(cut_off))

    cv2.imshow("Zoom", cut_off)
    cv2.waitKey(1000)


if __name__ == "__main__":
    process()
    cv2.destroyAllWindows()
