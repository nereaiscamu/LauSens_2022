import PySimpleGUI as sg
from PIL import Image, ImageTk
import bluriness_metric
import control_flip_camera
import microflu
import imgproc
import PySpin
from matplotlib.figure import Figure
import os
import numpy as np
import cv2
import serial
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import BytesIO
import base64
import sys

# Arduino init
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1000)
# print(arduino) # Arduino info.

# Pump init
try:
    lsp = serial.Serial("COM4", 9600, timeout=1000)
    microflu.initialize_LSPOne(lsp)
except:
    print("Pump not connected")

# Move camera
def move(com):
    arduino.write(com.encode("ascii"))
    time.sleep(0.05)

def move_along_axis(pos_camera, dir, step_focus):
    # format :
    # delay (2 chars) + " " + focusStep (4 chars) + " " +  axisdirection (3 chars : x/y/z + fw/bw)
    # Example :
    # 04 0100 zfw
    # NEED TO ADD 0 IN FRONT TO HAVE GOOD FORMAT
    com = "04 " + str(step_focus).zfill(4) # TODO reduce ?
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


# Absolute path of this file folder
path = os.path.dirname(os.path.abspath(__file__))

# Logo
size = (100, 50)
im = Image.open(path + "/lausens.png")
im = im.resize(size, resample=Image.Resampling.BICUBIC)

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

# Size of zoomed image displayed
size_zoom = (200, 200)

# Size of image displayed
camera_img_size = (3648, 5472)
reducing_factor = 0.16
zoom_in = False
zoom_pos_0 = (0, 0)
zoom_pos_1 = (camera_img_size[1], camera_img_size[0])
tmp_zoom_pos_1 = (camera_img_size[1], camera_img_size[0])
time_zoom = time.time()

# Init camera
control_flip_camera.init_camera(cam)

# Layout
sens_us_logo = [
    [sg.Image(size=size, key='-LOGO-', background_color="white")]
]
explanations = [
    [sg.Text("Welcome on our user interface ! \nThis GUI aims at controlling our system made of microfluidics pump, an autofocusing microscope and an image processing to detect IL-6 spots.")]
]

tab_micro_flu = [[sg.Button("Sample measurement", key="sample_measurement",  pad=(10, 10, 10, 0)), sg.Button("Filling", key="filling_microflu")], 
        [sg.Button("FLUSH", key="full_flush_microflu",  pad=(10, 0, 0, 0)), sg.Button("flush", key="flush_microflu",  pad=(10, 0, 0, 0)), sg.Button("HALT", key="halt_microflu", pad=(10, 0, 0, 0)), sg.Button("Cont", key="cont_microflu"), sg.Button("zero", key="zero_micro")],
        [sg.Button("EmptyTrash", key="empty_trash")]]
tab_Autofocus = [[sg.Text(key='-TEXT_METRIC-')],
        [sg.Frame("x / y plan", pad = (10, 0), layout = [[sg.Button("↑", key='-UP-', pad=(25, 5, 0, 0))], [sg.Button("←", key='-LEFT-'), sg.Button("→", key='-RIGHT-')], [sg.Button("↓", key='-DOWN-', pad=(25, 5, 0, 0))], ]), 
        sg.Frame("z plan", pad = (10, 0), layout = [[sg.Button("↑", key='-UP2-', pad=(25, 5, 0, 0))], [], [sg.Button("↓", key='-DOWN2-', pad=(25, 5, 0, 0))], ])],
        [sg.T("\n", size=(20 , 1), key='-wait-msg-')],
        [sg.Button("Autofocus", key="Autofocus", pad=(10, 10) ), sg.Button("Set to 0", key="set_to_zero", pad=(10, 10)), sg.Button("Move to 0", key="move_to_zero", pad=(10, 10)), sg.Button("Reset", key="-reset_zoom-", pad=(10, 10) )], 
        ]
tab_img_processing = [[sg.Text("Numer of spot :"), sg.Spin([i for i in range(6)], initial_value=3, pad = (0, 10, 0, 0),key='-nbr_spot-', font=('Helvetica 12'), enable_events=True)], [sg.Text("Background number :"), sg.Spin([i for i in range(6)], initial_value=3, key='-nbr_bg-', font=('Helvetica 12'), enable_events=True)], [sg.Button("Live acquisition", key="acquisition",  pad=(10, 10)), sg.Button("Process", key="imgproc",  pad=(10, 10))]]


print_metric = [
    [sg.TabGroup([[sg.Tab("Microfluidics", tab_micro_flu), 
        sg.Tab("Autofocus", tab_Autofocus),
        sg.Tab("Image processing", tab_img_processing),
        ]], expand_x=True)],

    [sg.Text(' '*15 + '-'*15 + "   Camera settings   " + '-'*15)],
    [sg.Text("Step focus :"), sg.Spin([5*i for i in range(102)],
                                      initial_value=50, key='-STEP_FOCUS-', font=('Helvetica 12'), size=(3, 2)),
     sg.Text("Exposure time :"), sg.Spin([100*i for i in range(100, 200)],
                                         initial_value=10332, key='-EXP_TIME-', font=('Helvetica 12'), enable_events=True)
     ],

    [sg.Text("         Gain :"), sg.Spin([i/10 for i in range(100, 300)],
                                         initial_value=23.3, key='-GAIN-', font=('Helvetica 12'), enable_events=True)],
    [sg.Image(size=size_zoom, key='-IMAGE_ZOOM-')],
]
img_to_print = [
    # resized_width, resized_height
    # [sg.Image(size=(1000, 1000), key='-IMAGE2-')]
    [sg.Graph(  (int(camera_img_size[1]*reducing_factor), int(camera_img_size[0]*reducing_factor)), (0, camera_img_size[0]), (camera_img_size[1], 0), key='-GRAPH-', drag_submits=True, enable_events=True)]
]

# ----- Full layout -----
# Main layout
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
                  expand_x=True, size=(100, 575)),
    ]
]

# Layout to display plots
layout2 = [[sg.Canvas(key='figCanvas')], ]

sg.theme('SystemDefault')

AppFont = 'Any 10'
window = sg.Window("LauSens - Autofocus Interface",
                   layout, resizable=True, no_titlebar=False, auto_size_buttons=True, font=AppFont).Finalize()
window.maximize()

# window2 = sg.Window("LauSens - Autofocus Interface",
#                    layout2, resizable=True, no_titlebar=False, auto_size_buttons=True, font=AppFont).Finalize()
# window2.set_alpha(0)

image = ImageTk.PhotoImage(image=im)
window['-LOGO-'].update(data=image)
window['-TEXT_METRIC-'].update(
    "Bluriness metric for this image :\n" +
    "Laplacian variance measurement : NaN arb. \n" +
    "JPEG size measurement : NaN kB  \n\n" +
    "Image position (1 unit ≈ 0.65 μm) :\n(0, 0, 0)")

# Convert np array image to Tkinter Image
def _photo_image(image: np.ndarray):
    height, width = image.shape
    data = f'P5 {width} {height} 255 '.encode(
    ) + image.astype(np.uint8).tobytes()
    return ImageTk.PhotoImage(width=width, height=height, data=data, format='PPM')

# Compute and return bluriness of current image (sent by camera)
def get_bluriness_metric():
    image_result = cam.GetNextImage(1000)

    if image_result.IsIncomplete():
        raise Exception('Image incomplete with image status %d ...' %
                        image_result.GetImageStatus())

    else:
        image_data = image_result.GetNDArray()
        image_result.Release()

        # Save image
        # TOO SLOW BUT MORE ACCURATE
        """
        img = Image.fromarray(image_data)
        print("Saving ...")
        start_time = time.time()
        # TODO reduce compress_level -> faster but less precise
        img.save(path + "/tmp.png", compress_level=3)
        print(f"Done in {time.time() - start_time} sec")
        """

        # reduce image
        # - to display on interface
        # - bluriness metric computed on this image will be faster
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(
            image_data, (resized_height, resized_width))

        img = Image.fromarray(image_data)
        # TODO reduce compress_level -> faster but less precise
        img.save(path + "/tmp.png", compress_level=3)

        # --- ONLY DIFFERENCE WITH get_metric(): ---
        # Update image on interface (slow down)
        # img = _photo_image(image_data)
        # window['-IMAGE2-'].update(data=img)

        buffered = BytesIO()
        Image.fromarray(image_data).save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        window['-GRAPH-'].erase()
        window['-GRAPH-'].DrawImage(data = img_str, location = (camera_img_size[1], camera_img_size[0]))

        # window.refresh() # TODO

    # TODO Choose metric to use
    # return bluriness_metric.blurre_JPEG_size_b(path + "/tmp.png") / 8 / 1000
    return bluriness_metric.blurre_lapace_var(path + "/tmp.png")

# Estimate time taken to send command and to move motors given a step value
# Return value will be the time to wait after we send a command to move motor of this step


def estimate_step_time(step):
    # Empirical measure
    # step 200 takes around 5 sec => sleep of 6
    # step 100 takes around 3 sec => sleep of 4
    # step 20 takes around 2 sec => sleep of 3
    # TODO Optimize to have finer estimation
    time_for_step = 2
    time = int(time_for_step + step*1/70)
    return time

# Fast autofocus but can fall into a local maxima
# Principle :
# Measure bluriness above, below and current position and go to in the direction that increase sharpness
def autofocus_fast(pos_camera):
    optimum = False
    opt_val = 0
    # TODO Param 1 :
    step = 100  # Increase if focus is far
    # TODO Param 2 :
    # Time to wait after we send the command
    time_for_step = estimate_step_time(step)
    while optimum == False:
        print("Round")
        print("current : ", get_bluriness_metric())

        move_along_axis(pos_camera, "-UP2-", step)
        time.sleep(time_for_step)
        above = get_bluriness_metric()
        print("above : ", above)

        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(time_for_step)
        opt_val = get_bluriness_metric()
        print("current (opti) : ", opt_val)

        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(time_for_step)
        below = get_bluriness_metric()
        print("below : ", below)

        # Better to stay below (below has higher sharpness than current)
        # We stay in below position
        if below >= opt_val and above <= opt_val:
            pass
        # Better to go above (above has higher sharpness than current)
        # We move to above position
        elif above >= opt_val and below <= opt_val:
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(time_for_step)
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(time_for_step)
        # Better to stay (above nor below have higher sharpness than current)
        # So we go back to current position and reduce step
        else:
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(time_for_step)
            step = int(step / 2)

        # TODO Param 3 :
        if abs(above - below) < 3 or step < 10 or opt_val > 1500:  # Stopping conditions
            optimum = True

# Improved autofocus
def autofocus_simple(pos_camera):
    # Must move camera below focal point (to find maxima by left)
    step = 20
    time_for_step = estimate_step_time(step)

    down = False
    # TODO Param 1 :
    range_curve = 4  # Increase if very far autofocus
    while down == False:
        sharpness_values_by_z = np.array([])
        for i in range(range_curve):
            print(i)
            val = get_bluriness_metric()
            move_along_axis(pos_camera, "-DOWN2-", step)
            sharpness_values_by_z = np.concatenate(
                (sharpness_values_by_z, np.array([val])))
            time.sleep(time_for_step)

        # Testing
        # print(sharpness_values_by_z)

        if sharpness_values_by_z[0] > sharpness_values_by_z[range_curve - 1]:
            down = True

    # Testing
    # print("Under focus (went to much DOWN2)")

    # TODO Param 2 :
    range_curve = 16  # Must be > range_curve
    sharpness_values_by_z = np.array([])
    for i in range(range_curve):
        print(i)
        val = get_bluriness_metric()
        move_along_axis(pos_camera, "-UP2-", step)
        sharpness_values_by_z = np.concatenate(
            (sharpness_values_by_z, np.array([val])))
        time.sleep(time_for_step)

    # Testing
    # print(sharpness_values_by_z)

    # Back to best state
    estimate_focal_point = np.argmax(sharpness_values_by_z)
    assert (step*(range_curve - estimate_focal_point)) < 10000

    # Testing
    # print(estimate_focal_point)
    # print(range_curve - estimate_focal_point)

    move_along_axis(pos_camera, "-DOWN2-", step *
                    (range_curve - estimate_focal_point))
    time.sleep(time_for_step*(range_curve - estimate_focal_point))
    best = get_bluriness_metric()

    # Empirical compensation (we generally went to far)
    focus = False
    while focus == False:
        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(time_for_step)
        tmp = (get_bluriness_metric())
        if tmp > best:
            best = tmp
        else:
            move_along_axis(pos_camera, "-UP2-", step)
            focus = True

# Used to display plot on interface
class Canvas(FigureCanvasTkAgg):
    """
    Create a canvas for matplotlib pyplot under tkinter/PySimpleGUI canvas
    """

    def __init__(self, figure=None, master=None):
        super().__init__(figure=figure, master=master)
        self.canvas = self.get_tk_widget()
        self.canvas.pack(side='top', fill='both', expand=1)

# Autofocus based on paper
# TODO DO NOT USE STILL UNDER DEVELOPPMENT/TEST


def smart_z_stack(pos_camera):
    print("i)")
    range_first_curve = 16
    step = 20
    sharpness_values_by_z = np.array([])
    for i in range(range_first_curve):
        print(i)
        val = get_bluriness_metric()
        move_along_axis(pos_camera, "-UP2-", step)
        sharpness_values_by_z = np.concatenate(
            (sharpness_values_by_z, np.array([val])))
        time.sleep(3)

    # Back to initial state
    move_along_axis(pos_camera, "-DOWN2-", step*range_first_curve)
    assert (step*range_first_curve) < 10000
    time.sleep(6)

    print("ii)")
    range_second_curve = 8
    second_shorter_curve_by_z = np.array([])

    for i in range(range_second_curve):
        print(i)
        val = get_bluriness_metric()
        move_along_axis(pos_camera, "-UP2-", step)
        second_shorter_curve_by_z = np.concatenate(
            (second_shorter_curve_by_z, np.array([val])))
        time.sleep(3)

    # Back to initial state
    move_along_axis(pos_camera, "-DOWN2-", step*range_second_curve)
    time.sleep(6)

    fig = Figure()
    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("i) Sharpness curve")
    ax.plot(range(range_first_curve), sharpness_values_by_z)
    ax = fig.add_subplot(1, 2, 2)
    ax.set_title("ii) Second sharpness curve, to estimate backlash")
    ax.plot(range(range_second_curve), second_shorter_curve_by_z)
    fig.tight_layout()
    canvas = Canvas(fig, window2['figCanvas'].Widget)
    canvas.draw()
    # window2.set_alpha(1)
    # window2.refresh()

    backlash = 0
    tmp = round(np.abs(np.sum(second_shorter_curve_by_z -
                              sharpness_values_by_z[:range_second_curve])))
    for i in range(1, range_first_curve - range_second_curve - 1):
        print(i)
        if tmp > round(np.abs(np.sum(second_shorter_curve_by_z - sharpness_values_by_z[i:range_second_curve+i]))):
            backlash = i
            tmp = round(np.abs(np.sum(second_shorter_curve_by_z -
                                      sharpness_values_by_z[i:range_second_curve+i])))
    print("Backlash = ", backlash)

    print("iii)")
    focal_point_below_stack_ctr = True
    estimate_focal_point = np.argmax(sharpness_values_by_z)
    print("Estimated focal point : ", estimate_focal_point)
    below_val = 3

    while(focal_point_below_stack_ctr):
        # move to a position below
        if step*(estimate_focal_point - below_val) > 9999:
            raise Exception("Focal point is too far (TODO)")
        move_along_axis(pos_camera, "-UP2-", step *
                        (estimate_focal_point - below_val))

        time.sleep(6)
        # collect a stack of 9 images with their sharpness + z-position
        stack_9_img = np.array([])
        for i in range(9):
            print(i)
            val = get_bluriness_metric()
            move_along_axis(pos_camera, "-UP2-", step)
            stack_9_img = np.concatenate((stack_9_img, np.array([val])))
            time.sleep(3)

        fig.clear(True)
        ax = fig.add_subplot(2, 1, 1)
        ax.set_title("iii) Stack of 9 images")
        ax.margins(100, 0)
        ax.plot(range(9), stack_9_img)
        fig.tight_layout()
        canvas = Canvas(fig, window2['figCanvas'].Widget)
        canvas.draw()
        # window2.refresh()

        estimate_focal_point = np.argmax(stack_9_img[0])
        print("Estimated focal point : ", estimate_focal_point)

        # Testing
        # x = input() # gives time for debugging

        while(int(stack_9_img.shape[0]/2) < estimate_focal_point):
            # if above center of the stack, move up and collect another image
            move_along_axis(pos_camera, "-UP2-", step)
            time.sleep(3)
            val = get_bluriness_metric()
            stack_9_img = np.concatenate((stack_9_img, np.array([val])))
            stack_9_img = np.delete(stack_9_img, 0)
            estimate_focal_point = np.argmax(stack_9_img[0])

        if(int(stack_9_img.shape[0]/2) == estimate_focal_point):
            focal_point_below_stack_ctr = False

        print("Estimated focal point : ", estimate_focal_point)

        # Testing
        # x = input() # gives time for debugging


# Position of camera RELATIVE (when launching soft. position of camera is (0, 0, 0))
pos_camera = np.array([0, 0, 0])

# Live acquisition enable
live_acqu = False
acqu_step = 0
acqu_time = 0

# Motor moving
warning_msg = False
warn_time = 0

def move_to_zero():
    index_step = 0
    step_list = [500, 200, 50, 10, 5]
    while(pos_camera[0] != 0 or pos_camera[1] != 0):
        step_focus = step_list[index_step]
        print(step_focus)
        time_for_step = estimate_step_time(step_focus)
        while(pos_camera[0] < 0 and step_focus <= abs(pos_camera[0])):
            move_along_axis(pos_camera, "-LEFT-", step_focus)
            time.sleep(time_for_step)
        while(pos_camera[0] > 0 and step_focus <= abs(pos_camera[0])):
            move_along_axis(pos_camera, "-RIGHT-", step_focus)
            time.sleep(time_for_step)
        while(pos_camera[1] < 0 and step_focus <= abs(pos_camera[1])):
            move_along_axis(pos_camera, "-UP-", step_focus)
            time.sleep(time_for_step)
        while(pos_camera[1] > 0 and step_focus <= abs(pos_camera[1])):
            move_along_axis(pos_camera, "-DOWN-", step_focus)
            time.sleep(time_for_step)
        if ((step_focus > pos_camera[0] or step_focus > pos_camera[1]) and index_step <= len(step_list) - 2):
            index_step += 1

# Update/display image and compute/display both bluriness metrics (JPEG size and Laplacian variance) on interace
def update():
    image_result = cam.GetNextImage(1000)

    if image_result.IsIncomplete():
        raise Exception('Image incomplete with image status %d ...' %
                        image_result.GetImageStatus())

    else:
        image_data = image_result.GetNDArray()
        image_result.Release()

        global zoom_pos_0
        global zoom_pos_1

        if zoom_in == False:
            if abs(zoom_pos_1[0] - zoom_pos_0[0]) < 5 or abs(zoom_pos_1[1] - zoom_pos_0[1]) < 5:
                zoom_pos_0 = (0, 0)
                zoom_pos_1 = (camera_img_size[1], camera_img_size[0])
            elif zoom_pos_1[0] < zoom_pos_0[0] and zoom_pos_1[1] < zoom_pos_0[1]:
                tmp = zoom_pos_0
                zoom_pos_0 = zoom_pos_1
                zoom_pos_1 = tmp
            elif zoom_pos_1[0] > zoom_pos_0[0] and zoom_pos_1[1] < zoom_pos_0[1]:
                tmp = zoom_pos_0
                zoom_pos_0 = (zoom_pos_0[0], zoom_pos_1[1])
                zoom_pos_1 = (zoom_pos_1[0], tmp[1])
            elif zoom_pos_1[0] < zoom_pos_0[0] and zoom_pos_1[1] > zoom_pos_0[1]:
                tmp = zoom_pos_0
                zoom_pos_0 = (zoom_pos_1[0], zoom_pos_0[1])
                zoom_pos_1 = (tmp[0], zoom_pos_1[1])

            image_data = image_data[zoom_pos_0[1]:zoom_pos_1[1], zoom_pos_0[0]:zoom_pos_1[0]]
            image_data = cv2.resize(image_data, (camera_img_size[1],camera_img_size[0] ) )
        else: 
            cv2.line(image_data, zoom_pos_0, (zoom_pos_0[0], tmp_zoom_pos_1[1]), color = (255, 255, 255), thickness = 10)
            cv2.line(image_data, zoom_pos_0, (tmp_zoom_pos_1[0], zoom_pos_0[1]), color = (255, 255, 255), thickness = 10)
            cv2.line(image_data, tmp_zoom_pos_1, (zoom_pos_0[0], tmp_zoom_pos_1[1]), color = (255, 255, 255), thickness = 10)
            cv2.line(image_data, tmp_zoom_pos_1, (tmp_zoom_pos_1[0], zoom_pos_0[1]), color = (255, 255, 255), thickness = 10)

        # Save image
        # SLOW
        """
        img = Image.fromarray(image_data)
        print("Saving ...")
        start_time = time.time()
        # TODO reduce compress_level -> faster but less precise
        img.save(path + "/tmp.png", compress_level=3)
        print(f"Done in {time.time() - start_time} sec")
        """

        global live_acqu
        global acqu_time
        global acqu_step
        if live_acqu == True and time.time() - acqu_time >= 30:
            print("Saving image " + str(acqu_step) + " at time " + str(time.time() - acqu_time))
            Image.fromarray(image_data).save(path + "/img_proc/images/saved_img_" + str(acqu_step) +".png")
            acqu_step += 1
            acqu_time = time.time()
            if acqu_step >= 10:
                live_acqu = False
                acqu_step = 0
                acqu_time = 0

        image_center = (int(image_data.shape[0]/2), int(image_data.shape[1]/2))
        image_data_zoom = image_data[int(image_center[0] - 100):int(image_center[0] + 100), int(image_center[1] - 100):int(image_center[1] + 100)]
        image_data_zoom = cv2.resize(
            image_data_zoom, size_zoom)

        # Draw white rectangle (zoom loc)
        cv2.line(image_data, (int(image_center[1] - 100), int(image_center[0] - 100)), (int(image_center[1] -100), int(image_center[0] + 100)), color = (255, 255, 255), thickness = 10) 
        cv2.line(image_data, (int(image_center[1] - 100), int(image_center[0] - 100)), (int(image_center[1] +100), int(image_center[0] - 100)), color = (255, 255, 255), thickness = 10) 
        cv2.line(image_data, (int(image_center[1] + 100), int(image_center[0] + 100)), (int(image_center[1] -100), int(image_center[0] + 100)), color = (255, 255, 255), thickness = 10) 
        cv2.line(image_data, (int(image_center[1] + 100), int(image_center[0] + 100)), (int(image_center[1] +100), int(image_center[0] - 100)), color = (255, 255, 255), thickness = 10)

        # reduce image
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(
            image_data, (resized_height, resized_width))
        image_center = (int(image_data.shape[0]/2), int(image_data.shape[1]/2))


        # Testing
        # # to measure time to update (most of time taken is to save image for computing bluriness)
        # print("Saving ...")
        # img = Image.fromarray(image_data)
        # start_time = time.time()
        # TODO reduce compress_level -> faster but less precise
        # img.save(path + "/tmp.png", optimize=True, compress_level=1)
        # print(f"Done in {time.time() - start_time} sec")
        window['-TEXT_METRIC-'].update(
            # "Bluriness metric for this image :\n" +
            # "Laplacian variance measurement : " + str(bluriness_metric.blurre_lapace_var(path + "/tmp.png")) + " arb. \n" +
            # bits to kiloBytes
            # "JPEG size measurement : " + str(bluriness_metric.blurre_JPEG_size_b(path + "/tmp.png") / 8 / 1000) + " kB \n\n" +
            "Image position (1 unit ≈ 0.65 μm) :\n" + str(pos_camera) + " ≈ " + str(pos_camera * 0.65))

        # To display img after
        # img = _photo_image(image_data)
        img_zoom = _photo_image(image_data_zoom)

        buffered = BytesIO()
        Image.fromarray(image_data).save(buffered, format="PNG", compress_level = 1)  
        tmp = buffered.getvalue()
        img_str = base64.b64encode(tmp)
        del tmp
        buffered.close()
        del buffered
        window['-GRAPH-'].erase()
        window['-GRAPH-'].DrawImage(data = img_str, location = (0, 0))
        # window['-IMAGE2-'].update(data=img)
        window['-IMAGE_ZOOM-'].update(data=img_zoom) 
        

# Run the Event Loop
while True:
    update()
    
    test_time_1 = time.time()
    event, values = window.read(timeout = 200) # TODO Timeout opt (lower to have  but makes the program slower) : 50
    print(f"1) Done in {time.time() - test_time_1} sec")
    
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "Autofocus":  # Autofocus
        print("perform autofocus")
        # AUTOFOCUS ALGO TO CHOOSE :
        autofocus_simple(pos_camera)
        # autofocus_fast(pos_camera)

    elif event == "set_to_zero":  # Set current position to be the initial position
        print("perform set to 0")
        pos_camera = np.array([0, 0, 0])   

    elif event == "move_to_zero":  # Set current position to be the initial position
        print("perform move to 0")
        move_to_zero()

    elif event == "-reset_zoom-":
        print("reset zoom")
        zoom_pos_0 = (0, 0)
        zoom_pos_1 = (camera_img_size[1], camera_img_size[0])

    elif event == "acquisition":  # Image acquisition
        print("perform image acquisition")
        live_acqu = True
        acqu_step = 0
        acqu_time = time.time() - 30

    elif event == "imgproc":  # Image processing
        print("perform image processing")
        imgproc.process(path, window['-nbr_spot-'].get(), window['-nbr_bg-'].get())
    
    elif event == "full_flush_microflu":  # Microfluidics full flush
        print("perform full flush")
        microflu.clean_all(lsp)

    elif event == "flush_microflu":  # Microfluidics flush
        print("perform flush")
        microflu.clean_sample_cartridge_trash(lsp) # TODO verify

    elif event == "filling_microflu":  # Microfluidics filling
        print("perform filling")
        microflu.filling_pipes(lsp)

    elif event == "sample_measurement":  # Microfluidics sample_measurement
        print("perform sample measurement") # TODO verify
        microflu.dispense_blocking_and_sample(lsp)
        # microflu.sequential_dispense(lsp)

    elif event == "halt_microflu":  # Microfluidics flush 
        print("microfluidics halted")
        microflu.halt(lsp)

    elif event == "cont_microflu":
        print("continuing from halting point")
        microflu.continue_from_halt(lsp)

    elif event == "empty_trash":
        print("Emptying trash")
        microflu.empty_trash(lsp)

    elif event == "zero_micro":
        print("continuing zero")
        microflu.go_to_zero(lsp)

    elif event == "-EXP_TIME-":  # Exposure time
        control_flip_camera.configure_exposure(cam, window['-EXP_TIME-'].get())

    elif event == "-GAIN-":  # Gain
        control_flip_camera.configure_gain(cam, window['-GAIN-'].get())

    elif event in {"-LEFT-", "-RIGHT-", "-UP-", "-DOWN-", "-UP2-", "-DOWN2-"}:  # Arrows to move camera
        step_focus = window['-STEP_FOCUS-'].get()
        move_along_axis(pos_camera, event, step_focus)
        # sg.popup("Please wait motors !", title="Info", auto_close = True, auto_close_duration= estimate_step_time(step_focus))
        window['-wait-msg-'].update("Please wait motors !")
        warning_msg = True
        warn_time = time.time()
    elif values['-GRAPH-'] != (None, None) and  event != '__TIMEOUT__':
        if zoom_in == False and event == '-GRAPH-':
            zoom_pos_0 = values['-GRAPH-']
            zoom_in = True
        if zoom_in == True and event == '-GRAPH-':
            tmp_zoom_pos_1 = values['-GRAPH-']
        elif event == '-GRAPH-+UP' and time.time() - time_zoom > 1: 
            zoom_pos_1 = values['-GRAPH-']
            zoom_in = False
            time_zoom = time.time()

    if warning_msg == True and time.time() - warn_time >= estimate_step_time(step_focus):
        window['-wait-msg-'].update("\n")
        warning_msg = False
        warn_time = 0

# Pump go to zero
try:
    microflu.go_to_zero(lsp)
except:
    print("Pump not connected")

move_to_zero()

cam.EndAcquisition()
cam.DeInit()

del cam
cam_list.Clear()
system.ReleaseInstance()

window.close()
# window2.close()