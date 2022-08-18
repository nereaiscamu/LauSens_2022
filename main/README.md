# Main

In this folder you'll find all code to perform microfluidics, autofocus and image processing.

This is made of a simple interface (`gui.py` using PySimpleGUI) displaying image from microscope.

Using this interface you can :

- control the pump
- move camera and autofocus
- process spot images

### Tree

Files

- `README.md` : This file
- `gui.py` : Main program and software interface
- `bluriness_metric.py` : Bluriness metric API
- `control_flip_camera.py` : Flip BFS-U3-200S6M-C USB 3.1 Blackfly® S, Monochrome Camera API (to init. camera, to set gain and to set exposure time)
- `manual_focus.py` : Python script to move camera backward and forward (via input) for focusing. It also set the focus step.
- `microflu.py` : Python script to control pump
- `imgproc.py` : Python script to process images
- `lausens.png` : LauSens logo image
- `sensUs.png` : Sens'Us logo image
- `tmp.png` : Temporarily saved image (used by `gui.py` to compute its sharpness)
- `Journal of Microscopy - 2021 - Knapper - Fast high‐precision autofocus on a motorised microscope Automating blood sample.pdf` : Paper used for coding autofocusing (many thanks !)

Folder

- `sketch_may17a` : Arduino sketch for motor control (to be upload on arduino Nano)
- `Images` : all images from microscope in \_.fig \_.png or \_.jpg format
- `img_proc` : folder used to store images for processing

  - `images` : folder that contains stored images during live acquisition
  - `images_processed` : folder that contains processed images after image processing

- `processing` : folder used by image processing

- `tests` :
  - `bluriness-test.ipynb` : Testing file for testing bluriness metric
  - `pysimplegui_matplotlib_test.py` : Testing file for solving problem of using `matplotlib` with `PySimpleGUI`
  - `test.py` : CURRENTLY NOT WORKING (was previously working). Python script to move camera using sangaboard package (many thanks to https://openflexure.discourse.group/t/graphical-interface-for-motor-control/924)
  - `port.py` : Python script to list open or occupied serial port
  - `parameters_camera.png` : Capture from SpinView of empirically "good" parameters (gain and exposure time)

### Requirements

`Matplotlib, numpy, opencv-python, serial, simple-pyspin, PySimpleGUI, cv2pip install opencv-python` python packages

### How to use ?

Run follwoing command (i.e run `gui.py` from your favorite python3 environnment):

`python3 gui.py`
