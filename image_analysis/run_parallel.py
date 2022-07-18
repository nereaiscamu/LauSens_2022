#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run parallel

This file detects the creation of a new file in a folder, which is then uploaded.
It will run in parallel with the creation of these files, stacking them in the size of a window, running the preprocessing
of the images and analysing them in order to get a result in the form of percentage of pixels detected, that correspond
to an estimation of the number of AU-NP detected by the SenSwiss sensor 2021, based on SPR in AU-NHA.

Created on Fri Aug 27 11:11:05 2021

@author: janet
"""
             
import time
import matplotlib
import os
import pandas as pd
from watchdog.observers import Observer
from processing.preprocess import select_ROI_image, live_plot
from processing.processing_functions import select_ROI
import matplotlib.pyplot as plt
#matplotlib.use('TkAgg') # This is for Mac
import numpy as np
from processing.RunAnalysisHandler import RunAnalysisHandler
import keyboard
import sys
import pylab as pl
from IPython import display

#ROIs = [[3444, 2316,  480], [1096, 2484,  480], [2348, 1456,  480], [4352,  820,  480]]



def describe_folders():
    ORIGINAL_FOLDER = os.path.dirname(os.path.realpath(__file__))
    print('THIS IS ORIGINAL FOLDER PATH', str(ORIGINAL_FOLDER))
    IMG_FOLDER = os.path.abspath('images') #Folder where the images taken by the camera to be processed will be located
    IMG_PROCESSED_FOLDER = os.path.abspath('images_processed')  #Folder where the resulting images will be located
    DIR_ROI = os.path.abspath('focus')
    path = IMG_FOLDER
    os.chdir(path)
    dirs = sorted(filter(os.path.isdir, os.listdir(path)), key=os.path.getctime)
    os.chdir(ORIGINAL_FOLDER)
    DIR = os.path.join(IMG_FOLDER, dirs[-1]) # folder to look at. (I select the last one created)
    return ORIGINAL_FOLDER, IMG_PROCESSED_FOLDER, IMG_FOLDER, DIR_ROI, DIR


def press_ROIs(DIR_ROI, ORIGINAL_FOLDER, RADIUS = 200):
    """
    Function to select the ROIs (regions of interest), for which the analysis will be computed.
    It opens the image in DIR_ROI, you press the center where you want to locate the ROIs and returns the position and radius after closing the image.
    The last two ROIs selected will be used as background.
    :param DIR_ROI: folder where the images in which the spots are clearly seen are located (./focus)
    :param ORIGINAL_FOLDER: folder where this script is located
    :param RADIUS: radius of the ROI
    :return:
        ROIs :  array with x, y, radius of size (num_ROIs, 3)
    """
    ROI_path = select_ROI_image(DIR_ROI)  # selecting image to select ROI, getting path
    print('ROI PATH', ROI_path)
    os.chdir(ORIGINAL_FOLDER)  # going back to original working directory
    ROIs = select_ROI(ROI_path, RADIUS = RADIUS)
    time.sleep(1)
    return ROIs


def run_analysis(ROIs, IMG_FOLDER, DIR, window_size = 5, framerate = 2, threshold = 140):
    """
    This function sets the observer to a folder (DIR) and each time a new event is detected (ex. a new image in the folder),
    it will count it, load the image, stack it and run the preprocessing and analysis.
    This way, it can be run in parallel during the acquisition.
    When pressed 's', the results are saved in results.csv at DIR and the program is stopped.
    :param ROIs:  array with x, y, radius of size (num_ROIs, 3)
    :param window_size: number of frames over which computes averate filter
    :param IMG_FOLDER: folder where the images taken by the camera to be processed will be located (./images)
    :param framerate: time between images (s)
    :param DIR: folder that will be observed. Inside /images, the last one created
    :param threshold: threshold to which binarize
    :return:
    """

    # Observer for running the analysis
    observer = Observer()
    event_analysis_handler = RunAnalysisHandler(ROIs, window_size=window_size, IMG_FOLDER=IMG_FOLDER, framerate=framerate, threshold=threshold)  # create event handler
    observer.schedule(event_analysis_handler, path=DIR)  # set observer to use created handler in directory
    observer.start()  # creates a new thread
    print('OBSERVED FOLDER', DIR)
    print('Press ctrl+j or ctrl+c to exit and save the results')


    # sleep until keyboard interrupt, then stop + rejoin the observer
    results_list = []

    #fig,ax = plt.subplots(1,1)
    try:
        while True:
            time.sleep(0.1)  # keeps main thread running
            results_list = event_analysis_handler.get_result()
            #print(results_list, 'results_list')
            signal = [x[0] for x in results_list[1:]]
            foreground = [x[1] for x in results_list[1:]]
            background = [x[2] for x in results_list[1:]]
            timest = np.arange(0, framerate*len(foreground), framerate)
            #live_plot(timest, signal)

            #print('Foreground,len', foreground, len(foreground))
            #pl.clf()
            #pl.plot(timest, background)
            #display.display(pl.gcf())
            #display.clear_output(wait=True)
            #time.sleep(1.0)
            #plt.pause(10)  #aquest
            #plt.show()
            #plt.clf()
            if keyboard.is_pressed('ctrl+j'):  # if key 'ctrl+j' is pressed
                print('You Pressed a Key!')
                observer.stop()  # when program stops, it does some work before terminating the thread
                print('Last results list (you pressed "ctrl+j")', results_list)
                results_df = pd.DataFrame(results_list, columns=('Signal', 'Foreground', 'Background'))
                results_df.to_csv(str(DIR) + '/result.csv', index=True)
                concentration = event_analysis_handler.get_concentration()
                print('concentration', concentration)
                # saving results as csv
                print('Saving results as result.csv')
                results_df['Concentration'] = pd.Series([concentration for x in range(len(results_df.index))])
                results_df.to_csv(str(DIR)+'/result.csv', index=True)
                #quit()
                sys.exit()
                
    except (KeyboardInterrupt, SystemExit):  # When pressing ctrl-c (at the end of the acquisition)
        observer.stop()  # when program stops, it does some work before terminating the thread
        print('Last results list', results_list)
        results_df = pd.DataFrame(results_list, columns=('Signal', 'Foreground', 'Background'))
        results_df.to_csv(str(DIR) + '/result.csv', index=True)
        concentration = event_analysis_handler.get_concentration()
        print('concentration', concentration)
        # saving results as csv
        results_df['Concentration'] = pd.Series([concentration for x in range(len(results_df.index))])
        results_df.to_csv(str(DIR)+'/result.csv', index=True)
        #quit()
        sys.exit()
    observer.join() # is needed to proper end a thread for "it blocks the thread in which you're making the call, until (self.observer) is finished


    print('asdf', event_analysis_handler.get_result())
    quit()


def main():
    print('ep')
    ## 1. DESCRIBING FOLDERS
    ORIGINAL_FOLDER, IMG_PROCESSED_FOLDER, IMG_FOLDER, DIR_ROI, DIR = describe_folders()

    # 2. SELECTING ROI from last image created in folder ./focus
    ROIs = press_ROIs(DIR_ROI, ORIGINAL_FOLDER, RADIUS = 200)

    # 3. STARTING THE OBSERVER, PROCESSING AND ANALYSING: it will find any new images
    run_analysis(ROIs, IMG_FOLDER=IMG_FOLDER, DIR=DIR, window_size=5, framerate=2, threshold=140)



if __name__ == "__main__":
    print('hei')
    # execute only if run as a script
    main()



