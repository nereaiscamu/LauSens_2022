import numpy as np
import cv2

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


def draw_any_shape(img_path, reduce_factor = 0.15, nbr_point_p = 8):
    global nbr_point
    global point_matrix

    nbr_point = nbr_point_p
    img_raw = cv2.imread(img_path)
    img_dim = np.shape(img_raw)[:2]

    reduced_img_raw = cv2.resize(
        img_raw,
        (int(img_dim[1] * reduce_factor), int(img_dim[0] * reduce_factor)),
        interpolation=cv2.INTER_AREA,
    )
 
    point_matrix = np.zeros((nbr_point, 2), np.int32)
    drawAnyShape(reduced_img_raw)

    mask = np.zeros_like(reduced_img_raw)
    cv2.fillPoly(mask, pts=[point_matrix], color=(255, 255, 255))
    masked_img = cv2.bitwise_and(reduced_img_raw, mask)

    cv2.imshow("masked_img", masked_img)
    cv2.waitKey(5000)

    cv2.destroyAllWindows()
