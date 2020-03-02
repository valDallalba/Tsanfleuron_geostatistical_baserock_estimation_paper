#!/usr/bin/env python
# coding: utf-8

# # Generate test images and fake aquisition from the mnt data
class ProgressBar:
    '''
    Progress bar
    '''
    def __init__ (self, valmax, maxbar, title):
        if valmax == 0:  valmax = 1
        if maxbar > 200: maxbar = 200
        self.valmax = valmax
        self.maxbar = maxbar
        self.title  = title
    
    def update(self, val):
        import sys
        # format
        if val > self.valmax: val = self.valmax
        
        # process
        perc  = round((float(val) / float(self.valmax)) * 100)
        scale = 100.0 / float(self.maxbar)
        bar   = int(perc / scale)
  
        # render 
        out = '\r %20s [%s%s] %3d %%' % (self.title, '=' * bar, ' ' * (self.maxbar - bar), perc)
        sys.stdout.write(out)

import pickle
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import os
import georasters as gr
from random import seed
seed(1)
from random import random

import tkinter as tk
from tkinter import filedialog

# Intro :
# We define here the parameters, and the training image in which we will cut the data.
print('Select the TI to sample (.tiff format) : ')
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
#file_path = './datas/TI/MNT_2016_TI_Alt2.tif'

if os.path.isfile(file_path):
    print('Le fichier est présent. import')
    data_DEM = gr.from_file(file_path)
    (xmin, xsize, x, ymax, y, ysize) = data_DEM.geot

else:
    print('error, impossible to import image')
    quit()

print('------------ \n \n ')
numX = int(input("Dimension of the cutted image in X [m] : ") )
print('------------ \n \n ')
numY = int(input("Dimension of the cutted image in Y [m] : ") )

#Load the data
size_img = np.array([numX,numY])
print('------------ \n \n ')
number_of_aquisition_lines = int(input("Number of Fake Aquisition lines per image : ") )
print('------------ \n \n ')
define_border = bool(input("Define border of the image as hard data ? (True of False) : ") )
error = 2
print('------------ \n \n ')
num_img = int(input("Number of simulations :") )



print('Sizes Infos :')

print(data_DEM.geot)
print(data_DEM.shape)
x_v = np.array(range(data_DEM.shape[1]))*2 + data_DEM.geot[3]
y_v = np.array(range(data_DEM.shape[0]))*2 + data_DEM.geot[0]
Y_dem, X_dem = np.meshgrid(x_v,y_v)

mask_where_nodata = data_DEM.raster != np.min(data_DEM.raster)


print('------------ \n \n ')
Bar = ProgressBar(num_img, 60, 'Generation of the images')

for lineit in range(num_img):

    Bar.update(lineit)

    res = False
    while res == False:
        size_img_c = (np.round(size_img / data_DEM.geot[1]))
        rdm_X = int(round(random()*(data_DEM.shape[1] - size_img_c[0])))
        rdm_Y = int(round(random()*(data_DEM.shape[0] - size_img_c[1])))

        box = [rdm_X, int(rdm_X+size_img_c[0]),rdm_Y,int(rdm_Y+size_img_c[1])]
        mask_cut = mask_where_nodata[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))]
        raster_cut = data_DEM.raster[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))]
        New_TI = np.array(data_DEM.raster)
        New_TI[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))] = data_DEM.nodata_value
        res = np.all(mask_cut)
        #a = np.ones(raster_cut.shape)*100000000
        
        mask = np.zeros(data_DEM.shape)
        mask[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))] = 1
            
    hard_data = pd.DataFrame()
    line = np.zeros([2,2])

    for i in range(number_of_aquisition_lines):

        top = [round(random()),round(random())]
        if top[0] == 1:  #Vertical start
            line[:,0] = np.array([round(random()*(box[1]-box[0]) + box[0]),box[2]])#return a x value, defined a y
        else:
            line[:,0] = np.array([box[0],round(random()*(box[3]-box[2]) + box[2])]) #return a x value, defined a y

        if top[1] == 1:
            line[:,1] = np.array([round(random()*(box[1]-box[0]) + box[0]),box[3]]) #return a x value, defined a y
        else:
            line[:,1] = np.array([box[1],round(random()*(box[3]-box[2]) + box[2])]) #return a x value, defined a y

        dx = np.int(np.max(np.diff(line)))

        x_pos = np.round(np.linspace(line[0,0],line[0,1],num =dx))
        y_pos = np.round(np.linspace(line[1,0],line[1,1],num =dx))

        d = {'cell_x': x_pos, 'cell_y': y_pos}
        pos_index = pd.DataFrame(d)
        pos_index["cell_x"] = pos_index["cell_x"].astype(int)
        pos_index["cell_y"] = pos_index["cell_y"].astype(int)
        pos_index['alt'] = data_DEM.raster[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['X'] = X_dem[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['Y'] = Y_dem[pos_index["cell_y"],pos_index["cell_x"]]

        hard_data = hard_data.append(pos_index, ignore_index = True)



    if define_border:
        x_cells = np.array(range(box[0],box[1]))
        y_cells = np.array(range(box[2],box[3]))
        
        x_pos = np.append(np.tile(x_cells,2),np.tile(x_cells[0],y_cells.size))#,)
        y_pos = np.append(np.tile(y_cells[0],x_cells.size),np.tile(y_cells[-1],x_cells.size))#)
        
        x_pos = np.append(x_pos,np.tile(x_cells[-1],y_cells.size))
        y_pos = np.append(y_pos,np.tile(y_cells,2))
        #x_pos = x_pos.append()
        
        d = {'cell_x': x_pos, 'cell_y': y_pos}
        pos_index = pd.DataFrame(d)
        pos_index["cell_x"] = pos_index["cell_x"].astype(int)
        pos_index["cell_y"] = pos_index["cell_y"].astype(int)
        
        pos_index['alt'] = data_DEM.raster[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['X'] = X_dem[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['Y'] = Y_dem[pos_index["cell_y"],pos_index["cell_x"]]
        
        hard_data = hard_data.append(pos_index, ignore_index = True)


    synthe_name = 'realisation' 
    save_path = './generated_data'
    if not(os.path.exists(save_path)):
        os.mkdir(save_path)
    elif lineit == 0:
        for root, dirs, files in os.walk(save_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            
        os.rmdir(save_path)
        os.mkdir(save_path)

    with open(save_path + '/' + synthe_name + str(lineit) + '.pickle', 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump([raster_cut.data, box, hard_data,New_TI,[mask,mask_where_nodata],None], f, pickle.HIGHEST_PROTOCOL)
        f.close()

print('------------ \n \n ')
print('Success !')
print('\n \n ------------  ')

