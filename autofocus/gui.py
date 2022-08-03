import PySimpleGUI as sg
from PIL import Image, ImageTk
import bluriness_metric
import control_flip_camera
import PySpin
import matplotlib.pyplot as plt
import os
import numpy as np
import cv2
import serial
import time

# Arduino init
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
time.sleep(1)
print(arduino)

# Move camera
def move(com):
    arduino.write(com.encode("ascii"))
    time.sleep(0.05)

def move_along_axis(pos_camera, dir, step_focus):
    com = "04 " + str(step_focus).zfill(4)
    if dir == "-LEFT-":
        com += " xfw"
        pos_camera += np.array([step_focus, 0, 0])
    elif dir == "-RIGHT-":
        com += " xbw"
        pos_camera -= np.array([step_focus, 0, 0])
    elif dir == "-UP-":
        com += " yfw"
        pos_camera += np.array([0, step_focus, 0])
    elif dir == "-DOWN-":
        com += " ybw"
        pos_camera -= np.array([0, step_focus, 0])
    elif dir == "-UP2-":
        com += " zfw"
        pos_camera += np.array([0, 0, step_focus])
    else:  # -DOWN2-
        com += " zbw"
        pos_camera -= np.array([0, 0, step_focus])
    move(com)

# Absolute path of this file
path = os.path.dirname(os.path.abspath(__file__))  

# Logo
size = (100, 50)
im = Image.open(path + "/sensUs.png")
im = im.resize(size, resample=Image.BICUBIC)

# Video / Image stream
print("Connection with camera")
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
num_cameras = cam_list.GetSize()
if num_cameras != 1:  # No camera or more than one camera
    cam_list.Clear()
    system.ReleaseInstance()
    raise Exception('Single camera not detected')
cam = cam_list[0]

# Init camera
control_flip_camera.init_camera(cam)

sens_us_logo = [
    [sg.Image(size=size, key='-LOGO-')]
]

explanations = [
    [sg.Text("Explanations : Welcome to auto-focus user interface !")]
]

print_metric = [
    [sg.Text(key='-TEXT_METRIC-')],
    [sg.Button("↑", pad=(25, 0, 0, 0), key='-UP-'),
    sg.Button("↑", pad=(10, 0, 0, 0), key='-UP2-')],
    [sg.Button("←", key='-LEFT-'), sg.Button("→", key='-RIGHT-')],
    [sg.Button("↓", key='-DOWN-', pad=(25, 0, 0, 0)),
    sg.Button("↓", pad=(10, 0, 0, 0), key='-DOWN2-')],
    [sg.Text('_'*15)],
    [sg.Text("Parameters :")],
    [sg.Text("Step focus :"), sg.Spin([10*i for i in range(21)],
                                           initial_value=50, key='-STEP_FOCUS-', font=('Helvetica 12'), size = (3, 2)), 
     sg.Text("Exposure time :"), sg.Spin([100*i for i in range(100, 200)],
                                           initial_value=10332, key='-EXP_TIME-', font=('Helvetica 12'), change_submits = True)
                                           ],

    [sg.Text("         Gain :"), sg.Spin([i/10 for i in range(100, 300)],
                                           initial_value=23.3, key='-GAIN-', font=('Helvetica 12'), change_submits = True)],
    [sg.Text('_'*23)],
    [sg.Button("AUTO-FOCUS", key="Autofocus")],
]

img_to_print = [
    [sg.Image(size=(300, 500), key='-IMAGE2-')]
]


# ----- Full layout -----
layout = [
    [
        sg.Column(sens_us_logo),
        sg.VSeperator(),
        sg.Column(explanations, element_justification='left',
                  expand_x=True, size=(100, 50)),
    ],
    [
        sg.Column(img_to_print),
        sg.VSeperator(),
        sg.Column(print_metric, element_justification='left',
                  expand_x=True, size=(100, 400)),
    ]
]

sg.theme('SystemDefault')

window = sg.Window("LauSens - Autofocus Interface",
                   layout, resizable=True, no_titlebar=False, auto_size_buttons=True).Finalize()

image = ImageTk.PhotoImage(image=im)
window['-LOGO-'].update(data=image)
window['-TEXT_METRIC-'].update(
    "Bluriness metric for this image :\n" +
    "Laplacian variance measurement : NaN arb. \n" +
    "JPEG size measurement : NaN kB  \n\n" +
    "Image position :\n(0, 0, 0)\n")


def _photo_image(image: np.ndarray):
    height, width = image.shape
    data = f'P5 {width} {height} 255 '.encode(
    ) + image.astype(np.uint8).tobytes()
    return ImageTk.PhotoImage(width=width, height=height, data=data, format='PPM')


def get_metric():
    image_result = cam.GetNextImage(1000)
    if image_result.IsIncomplete():
        raise Exception('Image incomplete with image status %d ...' %
                        image_result.GetImageStatus())
    else:
        image_data = image_result.GetNDArray()

        # reduce image
        reducing_factor = 0.15
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(image_data, (resized_height, resized_width))

        img = Image.fromarray(image_data)
        img.save(path + "/tmp.png", compress_level=1)
    image_result.Release()
    return bluriness_metric.blurre_lapace_var(path + "/tmp.png")


def autofocus_simple(pos_camera):
    optimum = False
    opt_val = 0
    step = 100
    while optimum == False:
        print("start")
        print("current : ", get_metric())

        move_along_axis(pos_camera, "-UP2-", step)
        time.sleep(5)
        above = get_metric()
        print("above : ", above)

        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(5)
        opt_val = get_metric()
        print("current (opti) : ", opt_val)

        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(5)
        below = get_metric()
        print("below : ", below)

        if below >= opt_val and above <= opt_val:
            pass
        elif above >= opt_val and below <= opt_val:
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(5)
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(5)
        else:
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(5)
            step = int(step / 2)

        if abs(above - below) < 0.5:
            optimum = True


pos_camera = np.array([0, 0, 0])

def update():
    image_result = cam.GetNextImage(1000)

    if image_result.IsIncomplete():
        raise Exception('Image incomplete with image status %d ...' %
                        image_result.GetImageStatus())

    else:
        image_data = image_result.GetNDArray()

        # Save image
        # SLOW
        """
        img = Image.fromarray(image_data)
        print("Saving ...")
        start_time = time.time()
        img.save(path + "/tmp.png", compress_level=3)
        print(f"Done in {time.time() - start_time} sec")
        """

        # reduce image
        reducing_factor = 0.15
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(
            image_data, (resized_height, resized_width))

        
        img = Image.fromarray(image_data)
        print("Saving ...")
        start_time = time.time()
        img.save(path + "/tmp.png", compress_level=3)
        print(f"Done in {time.time() - start_time} sec")
        

        window['-TEXT_METRIC-'].update(
            "Bluriness metric for this image :\n" +
            "Laplacian variance measurement : " + str(bluriness_metric.blurre_lapace_var(path + "/tmp.png")) + " arb. \n" +
            # bits to kiloBytes
            "JPEG size measurement : " + str(bluriness_metric.blurre_JPEG_size_b(path + "/tmp.png") / 8 / 1000) + " kB \n\n" +
            "Image position :\n" + str(pos_camera) + "\n")

        # To display img after
        img = _photo_image(image_data)

    image_result.Release()

    window['-IMAGE2-'].update(data=img)


# Run the Event Loop
while True:
    update()
    event, values = window.read(timeout=3000)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "Autofocus":
        print("perform autofocus")
        autofocus_simple(pos_camera)

    elif event == "-EXP_TIME-":
        control_flip_camera.configure_exposure(cam, window['-EXP_TIME-'].get())

    elif event == "-GAIN-":
        control_flip_camera.configure_gain(cam, window['-GAIN-'].get())

    elif event in {"-LEFT-", "-RIGHT-", "-UP-", "-DOWN-", "-UP2-", "-DOWN2-"}:
        step_focus = window['-STEP_FOCUS-'].get()
        move_along_axis(pos_camera, event, step_focus)

cam.EndAcquisition()
cam.DeInit()

del cam
cam_list.Clear()
system.ReleaseInstance()

window.close()
