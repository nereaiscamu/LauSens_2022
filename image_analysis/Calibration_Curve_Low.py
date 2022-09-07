# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 10:25:13 2022

@author: nerea
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from Nc_functions import *



#path = '/Users/karimzahra/Desktop/LauSens_2022/image_analysis/Results_Calib'

path = 'C:/Users/nerea/OneDrive/Documentos/EPFL_MASTER/MA2/SensUs/Results_600_Low'

#%%

#files = sorted(filter(os.path.isfile, os.listdir(path)), key=os.path.getctime)  # ordering the images by date of creation
files = sorted(os.listdir(path))  # ordering the images by name

#imgs = np.zeros((len(files), 3648, 5472))  # list with all the images (jpg or png). TODO: set to size of image
results = []
for i, filename in enumerate(files):
    print('Importing file  number '+ str(i) + ' ' + filename)
    results.append(np.loadtxt(os.path.join(path,filename))) #, delimiter=",",dtype='int'))

for i in range(len(results)):
    if len(results[i])>120:
        results[i] = results[i][:120]
        
# #%%       
# colors = ['c', 'r', 'r', 'b', 'b', 'k', 'k', 'k', 'k', 'm', 'm', 'g', 'g', 'g']
# results2 = []
# names = [] 
# for i in range(len(results)-1):
#     if files[i].split('_')[0] == files[i+1].split('_')[0]:
#         res= np.mean(results[i:i+1], axis = 0)
#         results2.append(res)
#         i += 1
#         name = files[i].split('_')[0]
#         names.append(name)     
#         plt.plot(np.arange(0, len(res)), res-res[0], colors[i], label = name)
       
#     if i>0 and (files[i-1].split('_')[0] == files[i].split('_')[0]) :
#         i+=1
             
#     else :
#         name = files[i].split('_')[0]
#         names.append(name)
#         results2.append(results[i])
#         plt.plot(np.arange(0, len(results[i])), results[i]-results[i][0], colors[i], label = name)
# plt.legend(fontsize = 'small')
# plt.show()  


#%%
import pandas as pd
names_all = np.array(files[i].split('p')[0] for i in range(len(files)))
a = pd.DataFrame(results)

a['concentration'] = names_all
a['concentration'] = a['concentration'].astype('int')

b = a.groupby('concentration').median().reset_index()
b.sort_values('concentration')
d = a.groupby('concentration').std().reset_index()
d.sort_values('concentration')

#%%
c = np.array(b)
d = np.array(d) 
labels = b['concentration']
cols = ['c', 'r', 'b', 'k',  'm', 'g', 'y', 'k']

for i in range(np.shape(c)[0]):
    # plt.plot(np.arange(0, (np.shape(c)[1]-1)), c[i,1:]-c[i,1] + d[i,1:], cols[i], label = c[i,0])
    # plt.plot(np.arange(0, (np.shape(c)[1]-1)), c[i,1:]-c[i,1] - d[i,1:], cols[i], label = c[i,0])
    plt.plot(np.arange(0, (np.shape(c)[1]-1)), c[i,1:]-c[i,1], cols[i], label = c[i,0])
    
plt.legend(fontsize = 'small')
plt.show()  
plt.savefig()

#%% 
 
# slopes= []
# r2s = []
# concentrations = np.array([0,1,2,5,3,4])

# 
# slopes = np.zeros(6)
# init = []

# for i, num in enumerate(concentrations):
#     slope, R = linear_model(results2[num], 10)
#     j = 1
#     while j< 3 and R<0.9  :
#         print(R)
#         print(j)
#         slope, R = linear_model(results2[num], starts[j])
#         j +=1
#     slopes[i]= slope
#     r2s.append(R)
            
# plt.xticks(concentrations, names)    
# plt.plot(slopes)
# plt.show()

#%%

# slopes= []
# r2s = []

# starts = [10, 20, 30]
# slopes = np.zeros(6)
# init = []

# for i in range(len(c)):
#     slope, R = linear_model(c[i,1:], 10)
#     j = 1
#     while j< 3 and R<0.9  :
#         slope, R = linear_model(c[i,1:], starts[j])
#         j +=1
#     slopes[i]= slope
#     print(slope)
#     r2s.append(R)
    
#%%
r2s = []
starts = [20, 30, 40, 50]
slopes2 = np.zeros(5)
a = np.array(a)

for i in range(len(a)):
    slope, R = linear_model(a[i,:-1], 20)
    j = 1
    while j< 4 and R<0.9  :
        slope, R = linear_model(a[i,:-1], starts[j])
        j +=1
    slopes2[i]= slope
    print(slope)
    r2s.append(R)

#%%


# plt.scatter(slopes, c[:,0], marker = "s")
# plt.show()

#%%
def linear_model_2(slopes, concentrations):
    model = LinearRegression()
    x = slopes.reshape(-1, 1)
    y = concentrations.reshape(-1, 1)
    model.fit(x, y)
    r_sq = model.score(x, y)
    print(f"slope: {model.coef_}")
    print(f"intercept: {model.intercept_}")
    print(f"coefficient of determination: {r_sq}")
    y_pred = model.predict(x)
    plt.scatter(x, y, color="black")
    plt.plot(x, y_pred, color="blue", linewidth=3)
    plt.show()
    return(model.coef_, r_sq)

# slope_calib, R_calib = linear_model_2(slopes, c[:,0])
# print(R_calib)

#%%

slope_calib2, R_calib2 = linear_model_2(slopes2, a[:,-1])
print(R_calib2)






