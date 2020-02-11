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
nbReal = int(input('How many MPS realisation by simulation set ? : '))
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

#Simulation
for name in data_name:
    #Load Data
    trueMNT, position, hd_df, ti = read_data(dir_path, name)
    
    #Simu1 zone + TI  
    mask_ti = create_mask_ti('ti_alt1_alti3d.pickle')
    hd_pts  = create_hd(hd_df)
    ti_img  = create_ti(ti)
    #simu1   = deeSse_run_ti(ti_img, mask_ti, hd_pts, n=n, t=t, f=f, nReal = nbReal)
    #extr1   = extract_simu_zone(simu1,position)
    
    #Simu2 zone + TI + Pyramide
    simu2   = deeSse_run_ti_pyr(ti_img, mask_ti, hd_pts, n=n, t=t, f=f, nReal = nbReal)
    extr2   = extract_simu_zone(simu2,position)
    
    #Simu3 zone
    mask_zone = create_mask_zone('ti_alt1_alti3d.pickle',position)
    #simu3     = deeSse_run_zone(ti_img, mask_zone, hd_pts, n=n, t=t, f=f, nReal = nbReal)
    #extr3     = extract_simu_zone(simu3,position) 

    #Simu4 zone + Pyramide
    simu4   = deeSse_run_zone_pyr(ti_img, mask_zone, hd_pts, n=n, t=t, f=f, nReal = nbReal)
    extr4   = extract_simu_zone(simu4,position)
    
    with open(save_path+'/'+name[:-7]+'_simu.pickle','wb') as file:
        pickle.dump([trueMNT,[extr2,extr4]],file, pickle.HIGHEST_PROTOCOL)

    
print('------------ \n \n ')
print('Success !')
print('\n \n ------------  ')