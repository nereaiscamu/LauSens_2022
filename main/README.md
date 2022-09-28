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
- `clean_img.py` : Python script to process images to remove images outilers (not used)
- `lausens.png` : LauSens logo image
- `sensUs.png` : Sens'Us logo image
- `tmp.png` : Temporarily saved image (used by `gui.py` to compute its sharpness)
- `Journal of Microscopy - 2021 - Knapper - Fast high‐precision autofocus on a motorised microscope Automating blood sample.pdf` : Paper used for coding autofocusing (many thanks !)

Folder

- `sketch_may17a` : Arduino sketch for motor control (to be upload on arduino Nano)
- `images` : images blurred and sharped
- `img_proc` : folder used to store images for processing

  - `images` : folder that contains stored images during live acquisition (5 consecutive images deleted within 10 sec)
  - `images_processed` : folder that contains processed images after image processing (median of those 5 consecutive images)
  - `saved_img` : folder that contains saved imaged with right clic on user interface
  - `results` : results obtained afer clicking on image processing with GUI

- `processing` : folder used by image processing

### Requirements

`Matplotlib, numpy, opencv-python, serial, simple-pyspin, PySimpleGUI, cv2` python packages

### How to use ?

Run follwoing command (i.e run `gui.py` from your favorite python3 environnment):

`python3 gui.py`
