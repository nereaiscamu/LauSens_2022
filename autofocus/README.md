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
- `sensUs.png` : Sens'Us logo image

Folder

- `Images` : all images from microscope in \_.fig \_.png or \_.jpg format

### Requirements

`Matplotlib, numpy, opencv-python` python packages

### How to use ?

Run follwoing command:

`python3 gui.py`
