# hello_psg.py

import PySimpleGUI as sg
from PIL import Image, ImageTk
import bluriness_metric
import PySpin
import matplotlib.pyplot as plt
import os
import numpy as np
import cv2

# Logo
size = (200, 100)

path = os.path.dirname(os.path.abspath(__file__))
im = Image.open(path + "/sensUs.png")
im = im.resize(size, resample=Image.BICUBIC)

# Video/ Image stream
system = PySpin.System.GetInstance()
version = system.GetLibraryVersion()
cam_list = system.GetCameras()
num_cameras = cam_list.GetSize()

if num_cameras != 1: # no camera or more than one camera
    cam_list.Clear()
    system.ReleaseInstance()
    raise Exception('Singe camera not detected')

cam = cam_list[0]
try:
    nodemap_tldevice = cam.GetTLDeviceNodeMap()
    cam.Init()
    nodemap = cam.GetNodeMap()

    sNodemap = cam.GetTLStreamNodeMap()
    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
    if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
        raise Exception('Unable to set stream buffer handling mode.. Aborting...')

    node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
    if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
        raise Exception('Unable to set stream buffer handling mode.. Aborting...')

    node_newestonly_mode = node_newestonly.GetValue()
    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

    node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
    if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
        raise Exception('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')

    # Retrieve entry node from enumeration node
    node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
    if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
            node_acquisition_mode_continuous):
        raise Exception('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')

    # Retrieve integer value from entry node
    acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

    # Set integer value from entry node as new value of enumeration node
    node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

    print('Acquisition mode set to continuous...')

    cam.BeginAcquisition()
    print('Acquiring images...')

    device_serial_number = ''
    node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
    if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
        device_serial_number = node_device_serial_number.GetValue()
        print('Device serial number retrieved as %s...' % device_serial_number)

except PySpin.SpinnakerException as ex:
        raise Exception('Error: %s' % ex)

# im2 = Image.open("images/blur_1.jpeg")

sens_us_logo = [
    [sg.Image(size=(300, 300), key='-LOGO-')]
]

explanations = [
    [sg.Text("Explanations : Welcome to auto-focus user interface !")]
]

print_metric = [
    [sg.Button("Update")],
    [sg.Text(key='-TEXT_METRIC-')],
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
                  expand_x=True, size=(100, 100)),

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
window['-TEXT_METRIC-'].update("Please browse and choose your file")

def _photo_image(image: np.ndarray):
    height, width = image.shape
    data = f'P5 {width} {height} 255 '.encode() + image.astype(np.uint8).tobytes()
    return ImageTk.PhotoImage(width=width, height=height, data=data, format='PPM')

# Run the Event Loop
while True:

    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "Update":
        # print(values["-IN-"])
        # im2 = Image.open(values["-IN-"])
        # image = ImageTk.PhotoImage(image=im2)

        image_result = cam.GetNextImage(1000)

        if image_result.IsIncomplete():
            raise Exception('Image incomplete with image status %d ...' % image_result.GetImageStatus())

        else:                    
            image_data = image_result.GetNDArray()

            # Save image
            img = Image.fromarray(image_data)
            img.save(path + "/tmp.png")
            # OR
            #save_img = ImageTk.getimage( img )
            #save_img.save(path + "/tmp.jpg") 
            #save_img.close()

            # reduce image
            reducing_factor = 0.1
            resized_width, resized_height = [int(i * reducing_factor) for i in image_data.shape]
            image_data=cv2.resize(image_data, (resized_height, resized_width))

            # To display img after
            img =  _photo_image(image_data) 

        image_result.Release()
        
        window['-IMAGE2-'].update(data=img)
        #window['-TEXT_METRIC-'].update(
        #    "Bluriness metric for this image :\n" +
        #    "Laplacian variance measurement : " + str(bluriness_metric.blurre_lapace_var(values["-IN-"])) + " arb. \n" +
        #    "JPEG size measurement : " + str(bluriness_metric.blurre_JPEG_size_b(values["-IN-"]) / 8 / 1000) + " kB \n")  # bits to kiloBytes

cam.EndAcquisition()
cam.DeInit()

del cam
cam_list.Clear()
system.ReleaseInstance()

window.close()
