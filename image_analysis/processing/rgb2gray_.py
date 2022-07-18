#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 16:46:47 2021

@author: janet
"""

from skimage.color import rgb2gray


path = '/Users/janet/EnginyeriaBiomèdica/MSc LIFE SCIENCES ENGINEERING/SensUs/Code/SensUs_2021_Code/test_preproc/Broken_screen'
imgs = [] # list with all the images (jpg or png)
time_creation = [] # list with the time of creation of each image
#parent = os.getcwd()
#path = os.path.join(parent, PATH)
print('\n Opening images '+str(path)+' ...')

os.chdir(path)  #TODO: NOT SURE ABOUT THIS
files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation

for filename in files:
#for filename in sorted(os.listdir(path)):
    if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
        img_path = os.path.join(path, filename)
        time_creation.append(os.stat(filename).st_ctime)
        #print(img_path)
        img = np.array(Image.open(img_path))
        imgs.append(rgb2gray(img)) #appending the image to the list
        
    else:
        continue
    
    


path = '/Users/janet/EnginyeriaBiomèdica/MSc LIFE SCIENCES ENGINEERING/SensUs/Code/SensUs_2021_Code/test_preproc/Broken_screen/BW'
for i in np.arange(0, len(imgs)):
    Image.fromarray(imgs[i]).save(os.path.join(path, str(i)+'.png'))