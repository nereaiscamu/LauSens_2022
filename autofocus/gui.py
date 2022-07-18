# hello_psg.py

import PySimpleGUI as sg
from PIL import Image, ImageTk
import bluriness_metric

# Logo
size = (200, 100)
im = Image.open("sensUs.png")
im = im.resize(size, resample=Image.BICUBIC)

# Video/ Image stream
imgPath = "images/blur_1.jpeg"
# im2 = Image.open("images/blur_1.jpeg")

sens_us_logo = [
    [sg.Image(size=(300, 300), key='-LOGO-')]
]

explanations = [
    [sg.Text("Explanations : Welcome to auto-focus user interface !")]
]

print_metric = [
    [sg.In(size=(25, 1)),
        sg.FileBrowse(key="-IN-"),
        sg.Button("Submit")],
    [sg.Text(key='-TEXT_METRIC-')],
]

img_to_print = [
    [sg.Image(size=(100, 100), key='-IMAGE2-')]
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

# Run the Event Loop
while True:

    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "Submit":
        # print(values["-IN-"])
        im2 = Image.open(values["-IN-"])
        image = ImageTk.PhotoImage(image=im2)
        window['-IMAGE2-'].update(data=image)
        window['-TEXT_METRIC-'].update(
            "Bluriness metric for this image :\n" +
            "Laplacian variance measurement : " + str(bluriness_metric.blurre_lapace_var(values["-IN-"])) + " arb. \n" +
            "JPEG size measurement : " + str(bluriness_metric.blurre_JPEG_size_b(values["-IN-"]) / 8 / 1000) + " kB \n")  # bits to kiloBytes

window.close()
