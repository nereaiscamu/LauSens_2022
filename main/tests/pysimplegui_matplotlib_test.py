# This script aims to test and solve problem of using matplotlib with PySimpleGUI
# When making a call to matplotlib like plt.plot this will reduce font size and rendering of PySimpleGUI windows

import PySimpleGUI as sg
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Thanks to 
# https://github.com/PySimpleGUI/PySimpleGUI/issues/5410
# https://towardsdatascience.com/integrating-pyplot-and-pysimplegui-b68be606b960

# VARS CONSTS:
_VARS = {'window': False, 'window2': False}

class Canvas(FigureCanvasTkAgg):
    """
    Create a canvas for matplotlib pyplot under tkinter/PySimpleGUI canvas
    """
    def __init__(self, figure=None, master=None):
        super().__init__(figure=figure, master=master)
        self.canvas = self.get_tk_widget()
        self.canvas.pack(side='top', fill='both', expand=1)

layout = [[sg.Canvas(key='figCanvas')],
          [sg.Button('Plot', key="-BUTTON-"), sg.Button('Exit')]]
layout2 = [[sg.Text("hello")],
          [sg.Button('Exit')]]

_VARS['window'] = sg.Window('Such Window',
                            layout,
                            finalize=True,
                            resizable=True,
                            element_justification="right")
_VARS['window2'] = sg.Window('Such Window',
                            layout2,
                            finalize=True,
                            resizable=True,
                            element_justification="right")

# Make synthetic data
dataSize = 1000
xData = np.random.randint(100, size=dataSize)
yData = np.linspace(0, dataSize, num=dataSize, dtype=int)

while True:
    event, values = _VARS['window'].read(timeout=200)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == "-BUTTON-":
        # make fig and plot
        fig = Figure()
        ax = fig.add_subplot(1,1, 1)
        ax.plot(xData, yData, '.k')
        fig.tight_layout()
        canvas = Canvas(fig, _VARS['window']['figCanvas'].Widget)   # Create a canvas for matplotlib figure
        canvas.draw()                                               # Update matplotlib figure to canvas
        _VARS['window'].refresh()                                   # Update GUI
            

_VARS['window'].close()