# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 10:25:13 2022

@author: nerea
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from Nc_functions import *




path = "/Users/karimzahra/Desktop/LauSens_2022/image_analysis/Results_Calib"

#files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation
files = sorted(os.listdir('/Users/karimzahra/Desktop/LauSens_2022/image_analysis/Results_Calib'))  # ordering the images by name

#imgs = np.zeros((len(files), 3648, 5472))  # list with all the images (jpg or png). TODO: set to size of image

results = []
for i, filename in enumerate(files):
    print('Importing file  number '+ str(i) + ' ' + filename)
    results.append(np.loadtxt(os.path.join(path,filename))) #, delimiter=",",dtype='int'))

for i in range(len(results)):
    if len(results[i])>60:
        results[i] = results[i][:60]
        
#%%       
colors = ['c', 'r', 'r', 'b', 'b', 'k', 'k', 'm', 'm', 'g', 'g']
results2 = []
names = []
std_res = [] 
for i in range(len(results)-1):
    if files[i].split('_')[0] == files[i+1].split('_')[0]:
        print(files[i].split('_')[0] + ' and ' + files[i+1].split('_')[0] )
        print(i)  
        res= np.mean(results[i:i+2], axis = 0)
        std = np.std(results[i:i+2], axis = 0)
        results2.append(res)
        std_res.append(std)
        i += 1
        name = files[i].split('_')[0]
        names.append(name)     
        plt.plot(np.arange(0, len(res)), res-res[0], colors[i], label = name)
        plt.plot(np.arange(0, len(res)), res-res[0] + std, colors[i], label = name)
        plt.plot(np.arange(0, len(res)), res-res[0] - std, colors[i], label = name)
       
    if i>0 and (files[i-1].split('_')[0] == files[i].split('_')[0]) :
        i+=1
             
    else :
        name = files[i].split('_')[0]
        names.append(name)
        results2.append(results[i])
        plt.plot(np.arange(0, len(results[i])), results[i]-results[i][0], colors[i], label = name)
plt.legend(fontsize = 'small')
plt.show()  


    
#%%   
 
slopes= []
r2s = []
concentrations = np.array([0,1,2,5,3,4])

starts = [10, 20, 30]
slopes = np.zeros(6)
init = []

for i, num in enumerate(concentrations):
    slope, R = linear_model(results2[num], 10)
    j = 1
    while j< 3 and R<0.9  :
        print(R)
        print(j)
        slope, R = linear_model(results2[num], starts[j])
        j +=1
    slopes[i]= slope
    r2s.append(R)
            
plt.xticks(concentrations, names)    
plt.plot(slopes)
plt.show()



#%%

