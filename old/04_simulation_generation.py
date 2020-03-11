#!/usr/bin/env python
# coding: utf-8
        
import pickle
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import os
import time 
from random import seed
seed(1)
from random import random

import tkinter as tk
from tkinter import filedialog

from geone import img
import geone.imgplot as imgplt
import geone.customcolors as ccol
import geone.deesseinterface as dsi

import geone.covModel as gcm
import geone.customcolors as ccol
from geone import grf


#Load Data
exec(open('./functions/04_function.py').read())
root = tk.Tk()
root.withdraw()

dir_path = filedialog.askdirectory()

if os.path.isdir(dir_path):
    print('The folder is a valid folder')
    
    data_name = os.listdir(dir_path)
    if len(data_name) == 0:
        print('The folder is empty.')
        quit()
        
else:
    print('not a directory')
    quit()

    
#DeeSse parameters
nbReal = int(input('How many realisation by simulation set ? : '))
para_b = str(input('Do you want to use the deeSse parameters set by default (n=12, t=0.005, f=0.5)? (True or False) : '))

if para_b == 'False':
    print('Set up the deeSse parameters : ')
    n = int(input('n : '))
    t = float(input('t : '))
    f = float(input('f : '))
    
else:
    print('Default parameters are used.')
    n, t, f = 12, 0.005, 0.5
    
#Save the data
save_path = './simulation_output'

if not(os.path.exists(save_path)):
        os.mkdir(save_path)
else: 
    for root, dirs, files in os.walk(save_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
            
        os.rmdir(save_path)
        os.mkdir(save_path)

rangeM = int(input('Define the range of the model (default value recommended is 500) : '))
sillM  = int(input('Define the sill of the model (default value recommended is 1400) : '))
print('The default model is set to be spherical.')

cov_model = gcm.CovModel2D(elem=[
    ('spherical', {'w':rangeM, 'r':[sillM]}), # elementary contribution
                       ], alpha=0, name='model-2D test')        

cov_fun   = cov_model.func()
vario_fun = cov_model.vario_func()


#Simulation
for name in data_name:
        #Load Data
    trueMNT, position, hd_df, ti = read_data(dir_path, name)
    ti[ti == np.min(np.min(ti)) ] = np.nan
    
    #Load Data
    trueMNT, position, hd_df, ti = read_data(dir_path, name)
    
    #Simu1 zone + TI  
    mask_ti = create_mask_ti('ti_alt2_alti3d.pickle')
    hd_pts  = create_hd(hd_df)
    ti_img  = create_ti(ti)
    
    
    #Simu2 zone + TI + Pyramide
    simu2   = deeSse_run_ti_pyr(ti_img, mask_ti, hd_pts, n=n, t=t, f=f, nReal = nbReal)
    extr2   = extract_simu_zone(simu2,position)
    
    #Simu3 zone
    mask_zone = create_mask_zone('ti_alt2_alti3d.pickle',position)
     

    #Simu4 zone + Pyramide
    simu4   = deeSse_run_zone_pyr(ti_img, mask_zone, hd_pts, n=n, t=t, f=f, nReal = nbReal)
    extr4   = extract_simu_zone(simu4,position)
    
    #GRF
    X,Y = create_hd_grf(hd_df,position)
    dimension, spacing, origin = create_grid(position)
    
    extensionMin = [grf.extension_min(r, n, s) for r, n, s in zip(cov_model.rxy(), dimension, spacing)]
    simGRF       = grf.grf2D(cov_fun, dimension, spacing, origin, x=X, v=Y, 
                   extensionMin=extensionMin, nreal=int(nbReal))
    
    krige, krige_std = grf.krige2D(X, Y, cov_fun, dimension, spacing, origin, 
                                   extensionMin=extensionMin)
        
    
    with open(save_path+'/'+name[:-7]+'_simu.pickle','wb') as file:
        pickle.dump([trueMNT,[extr2,extr4,simGRF]],file, pickle.HIGHEST_PROTOCOL)
        
    with open(save_path+'/'+name[:-7]+'_krige.pickle','wb') as file:
        pickle.dump([trueMNT,[krige, krige_std]],file, pickle.HIGHEST_PROTOCOL)

    
print('------------ \n \n ')
print('Success !')
print('\n \n ------------  ')