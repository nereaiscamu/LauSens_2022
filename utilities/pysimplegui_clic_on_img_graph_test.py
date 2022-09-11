import PySimpleGUI as sg
from PIL import Image, ImageTk
import time
import base64
from io import BytesIO
import os


"""
    Demo application to show how to draw rectangles and letters on a Graph Element
    This demo mocks up a crossword puzzle board
    It will place a letter where you click on the puzzle
"""


BOX_SIZE = 25

layout = [
    [sg.Text("Crossword Puzzle Using PySimpleGUI"), sg.Text("", key="-OUTPUT-")],
    [
        sg.Graph(
            (800, 800),
            (-50, -50),
            (50, 50),
            key="-GRAPH-",
            change_submits=True,
            drag_submits=False,
        )
    ],
    [sg.Button("Show"), sg.Button("Exit")],
]

window = sg.Window("Window Title", layout, finalize=True)

g = window["-GRAPH-"]

path = os.path.dirname(os.path.abspath(__file__))
img = Image.open(path + "/images/Frame_225_sharp.png")

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    mouse = values["-GRAPH-"]

    print("Saving ...")
    start_time = time.time()
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    print(f"Done in {time.time() - start_time} sec")
    g.DrawImage(data=img_str, location=(-50, 50))

    sg.popup_non_blocking(
        "Test for non blocking popup",
        title="Info",
        auto_close=True,
        non_blocking=True,
        auto_close_duration=10,
    )


window.close()
