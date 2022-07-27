# Auto-focus

In this folder you'll find all code to perform autofocus.

This is made of a simple interface (`gui.py` using PySimpleGUI), that prints one image and its bluriness.
Later on, this script will also (given images received by microscope) adapt it to automatically perform auto-focus by moving motors.

### Tree

Files

- `README.md` : This file
- `gui.py` : Main program and software interface
- `bluriness-test.ipynb` : Testing file for testing bluriness metric
- `bluriness_metric.py` : Bluriness metric API
- `manual_focus.py` : Python script to move camera backward and forward (via input) for focusing. It also set the focus step
- `test.py` : CURRENTLY NOT WORKING (was previously working). Python script to move camera using sangaboard package (many thanks to https://openflexure.discourse.group/t/graphical-interface-for-motor-control/924)
- `port.py` : Python script to list open or occupied serial port
- `sensUs.png` : Sens'Us logo image

Folder

- `sketch_may17a` : Arduino sketch for motor control (to be upload on arduino Nano)
- `Images` : all images from microscope in \_.fig \_.png or \_.jpg format

### Requirements

`Matplotlib, numpy, opencv-python` python packages

### How to use ?

Run follwoing command:

`python3 gui.py`
