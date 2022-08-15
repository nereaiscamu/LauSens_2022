import PySimpleGUI as sg
from PIL import Image, ImageTk
import bluriness_metric
import control_flip_camera
import PySpin
from matplotlib.figure import Figure
import os
import numpy as np
import cv2
import serial
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Arduino init
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
time.sleep(1)  # Needed so that computer detect arduino (TODO can reduce it ?)
# print(arduino) # Arduino info.

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
im = Image.open(path + "/lausens.png")
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

# Layout
sens_us_logo = [
    [sg.Image(size=size, key='-LOGO-', background_color="white")]
]
explanations = [
    [sg.Text("Explanations : Welcome to auto-focus user interface !")]
]
print_metric = [
    [sg.Text(key='-TEXT_METRIC-')],
    [sg.Button("↑", pad=(25, 0, 0, 0), key='-UP-'),
     sg.Button("↑", pad=(30, 0, 0, 0), key='-UP2-')],
    [sg.Button("←", key='-LEFT-'), sg.Button("→", key='-RIGHT-')],
    [sg.Button("↓", key='-DOWN-', pad=(25, 0, 0, 0)),
     sg.Button("↓", pad=(30, 0, 0, 0), key='-DOWN2-')],
    [sg.Text('_'*15)],
    [sg.Text("Parameters :")],
    [sg.Text("Step focus :"), sg.Spin([10*i for i in range(21)],
                                      initial_value=50, key='-STEP_FOCUS-', font=('Helvetica 12'), size=(3, 2)),
     sg.Text("Exposure time :"), sg.Spin([100*i for i in range(100, 200)],
                                         initial_value=10332, key='-EXP_TIME-', font=('Helvetica 12'), change_submits=True)
     ],

    [sg.Text("         Gain :"), sg.Spin([i/10 for i in range(100, 300)],
                                         initial_value=23.3, key='-GAIN-', font=('Helvetica 12'), change_submits=True)],
    [sg.Text('_'*23)],
    [sg.Button("AUTO-FOCUS", key="Autofocus"), sg.Button("IMG-PROC",
                                                         key="imgproc"), sg.Button("MICRO-FLU", key="microflu")],
]
img_to_print = [
    # resized_width, resized_height
    [sg.Image(size=(547, 820), key='-IMAGE2-')]
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
                  expand_x=True, size=(100, 400)),
    ]
]

# Layout to display plots
layout2 = [[sg.Canvas(key='figCanvas')], ]

sg.theme('SystemDefault')

AppFont = 'Any 10'
window = sg.Window("LauSens - Autofocus Interface",
                   layout, resizable=True, no_titlebar=False, auto_size_buttons=True, font=AppFont).Finalize()

window2 = sg.Window("LauSens - Autofocus Interface",
                    layout2, resizable=True, no_titlebar=False, auto_size_buttons=True, font=AppFont).Finalize()
window2.set_alpha(0)

image = ImageTk.PhotoImage(image=im)
window['-LOGO-'].update(data=image)
window['-TEXT_METRIC-'].update(
    "Bluriness metric for this image :\n" +
    "Laplacian variance measurement : NaN arb. \n" +
    "JPEG size measurement : NaN kB  \n\n" +
    "Image position (1 unit ≈ 0.65 μm) :\n(0, 0, 0)\n")

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
        reducing_factor = 0.15
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(
            image_data, (resized_height, resized_width))

        img = Image.fromarray(image_data)
        # TODO reduce compress_level -> faster but less precise
        img.save(path + "/tmp.png", compress_level=3)

        # --- ONLY DIFFERENCE WITH get_metric(): ---
        # Update image on interface (slow down)
        img = _photo_image(image_data)
        window['-IMAGE2-'].update(data=img)

        window.refresh()

    # TODO Choose metric to use
    # return bluriness_metric.blurre_JPEG_size_b(path + "/tmp.png") / 8 / 1000
    return bluriness_metric.blurre_lapace_var(path + "/tmp.png")

# Compute and return bluriness of current image (sent by camera)
# Same as get_bluriness_metric but doesn't update image (i.e not displayed on interface)
# TODO Remove get_metric() to have only get_bluriness_metric()


def get_metric():
    image_result = cam.GetNextImage(1000)
    if image_result.IsIncomplete():
        raise Exception('Image incomplete with image status %d ...' %
                        image_result.GetImageStatus())
    else:
        image_data = image_result.GetNDArray()
        image_result.Release()

        # reduce image
        reducing_factor = 0.15
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(image_data, (resized_height, resized_width))

        img = Image.fromarray(image_data)
        # TODO reduce compress_level -> faster but less precise
        img.save(path + "/tmp.png", compress_level=3)

    window.refresh()

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
    time_for_step = 3
    if step > 50:
        time_for_step = 4
    if step > 110:
        time_for_step = 5
    if step > 150:
        time_for_step = 6
    return time_for_step

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
        above = get_metric()
        print("above : ", above)

        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(time_for_step)
        opt_val = get_metric()
        print("current (opti) : ", opt_val)

        move_along_axis(pos_camera, "-DOWN2-", step)
        time.sleep(time_for_step)
        below = get_metric()
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
    window2.set_alpha(1)
    window2.refresh()

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
        window2.refresh()

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

# Update/display image and compute/display both bluriness metrics (JPEG size and Laplacian variance) on interace


def update():
    image_result = cam.GetNextImage(1000)

    if image_result.IsIncomplete():
        raise Exception('Image incomplete with image status %d ...' %
                        image_result.GetImageStatus())

    else:
        image_data = image_result.GetNDArray()
        image_result.Release()

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

        # reduce image
        reducing_factor = 0.15
        resized_width, resized_height = [
            int(i * reducing_factor) for i in image_data.shape]
        image_data = cv2.resize(
            image_data, (resized_height, resized_width))

        img = Image.fromarray(image_data)
        # Testing
        # # to measure time to update (most of time taken is to save image for computing bluriness)
        # print("Saving ...")
        # start_time = time.time()
        # TODO reduce compress_level -> faster but less precise
        img.save(path + "/tmp.png", compress_level=3)
        # print(f"Done in {time.time() - start_time} sec")

        window['-TEXT_METRIC-'].update(
            "Bluriness metric for this image :\n" +
            "Laplacian variance measurement : " + str(bluriness_metric.blurre_lapace_var(path + "/tmp.png")) + " arb. \n" +
            # bits to kiloBytes
            "JPEG size measurement : " + str(bluriness_metric.blurre_JPEG_size_b(path + "/tmp.png") / 8 / 1000) + " kB \n\n" +
            "Image position (1 unit ≈ 0.65 μm) :\n" + str(pos_camera) + " ≈ " + str(pos_camera * 0.65) + "\n")

        # To display img after
        img = _photo_image(image_data)

    window['-IMAGE2-'].update(data=img)


# Run the Event Loop
while True:
    update()
    event, values = window.read(timeout=3000)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "Autofocus":  # Autofocus
        print("perform autofocus")
        # AUTOFOCUS ALGO TO CHOOSE :
        autofocus_simple(pos_camera)
        # autofocus_fast(pos_camera)

    elif event == "imgproc":  # Image Processing
        print("perform image processing")
        # TODO: add IP code
        pass

    elif event == "microflu":  # Microfluidics
        print("perform microfluidics")
        # TODO: add microflu code
        pass

    elif event == "-EXP_TIME-":  # Exposure time
        control_flip_camera.configure_exposure(cam, window['-EXP_TIME-'].get())

    elif event == "-GAIN-":  # Gain
        control_flip_camera.configure_gain(cam, window['-GAIN-'].get())

    elif event in {"-LEFT-", "-RIGHT-", "-UP-", "-DOWN-", "-UP2-", "-DOWN2-"}:  # Arrows to move camera
        step_focus = window['-STEP_FOCUS-'].get()
        move_along_axis(pos_camera, event, step_focus)

cam.EndAcquisition()
cam.DeInit()

del cam
cam_list.Clear()
system.ReleaseInstance()

window.close()
window2.close()
