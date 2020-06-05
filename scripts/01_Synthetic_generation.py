#!/usr/bin/env python
# coding: utf-8

import pickle
import numpy as np
import pandas as pd
import os
import georasters as gr
from random import seed
seed(1)
from random import random

import tkinter as tk
from tkinter import filedialog


###########################################################
# Generate test images and fake aquisition from a mnt tif.
# Create to test the MPS parameters and compare the different 
# methods of simulation/estimation on the Tsanfleuron Glacier
# project.
# Alexis Neven 02/2020
###########################################################


#############
#Progress bar
#############
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

        
###########
# Load Data
###########

print('Select the TI to sample (.tiff format with no_value as a numerical values) : ')
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

    
##########
#Extraction parameters
##########

print('------------ \n \n ')
numX = int(input("Dimension of the cutted image in X [m] : ") )
print('------------ \n \n ')
numY = int(input("Dimension of the cutted image in Y [m] : ") )
size_img = np.array([numX,numY])

print('------------ \n \n ')
number_of_aquisition_lines = int(input("Number of Fake Aquisition lines per image : ") )
print('------------ \n \n ')
define_border = bool(input("Define border of the image as hard data ? (True of False) : ") )
print('------------ \n \n ')
num_img = int(input("Number of simulations :") )

print('Sizes Infos :')
print(data_DEM.geot)
print(data_DEM.shape)


##########
#Create the mask 
##########
x_v = np.array(range(data_DEM.shape[1]))*2 + data_DEM.geot[3]
y_v = np.array(range(data_DEM.shape[0]))*2 + data_DEM.geot[0]
Y_dem, X_dem = np.meshgrid(x_v,y_v)

mask_where_nodata = data_DEM.raster != np.min(data_DEM.raster)


#########
#Generation of the data
#########

print('------------ \n \n ')
Bar = ProgressBar(num_img, 60, 'Generation of the images')

for lineit in range(num_img):
     
    #update prograss bar
    Bar.update(lineit)
    
    #Extracted zone
    #(loop until the extracted zone does not conntains any no_data)
    res = False
    while res == False:
        
        #random location on the TI
        size_img_c = (np.round(size_img / data_DEM.geot[1]))
        rdm_X      = int(round(random()*(data_DEM.shape[1] - size_img_c[0])))
        rdm_Y      = int(round(random()*(data_DEM.shape[0] - size_img_c[1])))
        
        #cut the TI on the location and to its define size
        box        = [rdm_X, int(rdm_X+size_img_c[0]),rdm_Y,int(rdm_Y+size_img_c[1])] #xmin, xmax, ymin, ymax
        mask_cut   = mask_where_nodata[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))]
        raster_cut = data_DEM.raster[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))]
        
        #set as no_value the cutted part of the TI
        New_TI = np.array(data_DEM.raster)
        New_TI[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))] = data_DEM.nodata_value
        
        #test if all the selected cutted values are define
        res    = np.all(mask_cut)
        
        #create a geone mask for the simulation (0=outside, 1=inside)
        mask = np.zeros(data_DEM.shape)
        mask[rdm_Y:(rdm_Y+int(size_img_c[1])),rdm_X:int((rdm_X+size_img_c[0]))] = 1
        
            
    #Fake Hard data
    hd_df     = pd.DataFrame()
    line      = np.zeros((2,2))
    
    #Fake lines
    for i in range(number_of_aquisition_lines):

        top = [round(random()),round(random())]
        if top[0] == 1:  #Vertical start
            #return a x value, defined a y
            line[:,0] = np.array([round(random()*(box[1]-box[0]) + box[0]),box[2]])
        else: 
            #return a x value, defined a y
            line[:,0] = np.array([box[0],round(random()*(box[3]-box[2]) + box[2])])

        if top[1] == 1:
            #return a x value, defined a y
            line[:,1] = np.array([round(random()*(box[1]-box[0]) + box[0]),box[3]]) 
        else: 
            #return a x value, defined a y
            line[:,1] = np.array([box[1],round(random()*(box[3]-box[2]) + box[2])])

        dx    = np.int(np.max(np.diff(line)))
        x_pos = np.round(np.linspace(line[0,0],line[0,1],num =dx))
        y_pos = np.round(np.linspace(line[1,0],line[1,1],num =dx))

        d = {'cell_x': x_pos, 'cell_y': y_pos}
        pos_index = pd.DataFrame(d)
        pos_index["cell_x"] = pos_index["cell_x"].astype(int)
        pos_index["cell_y"] = pos_index["cell_y"].astype(int)
        pos_index['alt']    = data_DEM.raster[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['X']      = X_dem[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['Y']      = Y_dem[pos_index["cell_y"],pos_index["cell_x"]]

        hd_df = hd_df.append(pos_index, ignore_index = True)

    #Fake border
    if define_border:
        x_cells = np.array(range(box[0],box[1]))
        y_cells = np.array(range(box[2],box[3]))
        
        x_pos = np.append(np.tile(x_cells,2),np.tile(x_cells[0],y_cells.size))
        y_pos = np.append(np.tile(y_cells[0],x_cells.size),np.tile(y_cells[-1],x_cells.size))
        
        x_pos = np.append(x_pos,np.tile(x_cells[-1],y_cells.size))
        y_pos = np.append(y_pos,np.tile(y_cells,2))
        
        d = {'cell_x': x_pos, 'cell_y': y_pos}
        pos_index = pd.DataFrame(d)
        pos_index["cell_x"] = pos_index["cell_x"].astype(int)
        pos_index["cell_y"] = pos_index["cell_y"].astype(int)
        pos_index['alt']    = data_DEM.raster[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['X']      = X_dem[pos_index["cell_y"],pos_index["cell_x"]]
        pos_index['Y']      = Y_dem[pos_index["cell_y"],pos_index["cell_x"]]
        
        hd_df = hd_df.append(pos_index, ignore_index = True)

    #Save synthetic output
    synthe_name = 'realisation' 
    save_path   = '../generated_data'
    
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
        
    #Output data    
    trueMNT  = np.copy(raster_cut.data)
    position = np.copy(box)
    ti       = np.copy(New_TI)
    ti[ti==np.nanmin(ti)] = np.nan
    mask_box    = np.copy(mask)
    mask_box_ti = np.copy(data_DEM.raster.data)
    mask_box_ti[mask_box_ti == np.nanmin(mask_box_ti)] = 0
    mask_box_ti[mask_box_ti > np.nanmin(mask_box_ti)]  = 1    
    
    with open(save_path + '/' + synthe_name + str(lineit).zfill(2) + '.pickle', 'wb') as f:
        pickle.dump([trueMNT, position, hd_df, ti, mask_box, mask_box_ti], f, pickle.HIGHEST_PROTOCOL)
        
        
        
        
print('------------ \n \n ')
print('Success !')
print('\n \n ------------  ')

