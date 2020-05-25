#!/usr/bin/env python
# coding: utf-8
        
import pickle
import numpy as np
import pandas as pd
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


###################################################################
# Deesse, GRF and kriging simulation/estimation for the Tsanfleuron
# Glacier and the synthethic data associatied.
# Valentin Dall'alba 02/2020
###################################################################

##########
#Load Data
##########

exec(open('../functions/02_simulation_functions.py').read())
exec(open('../functions/02_kriging_functions.py').read())

print('Select the folder that contain the input file (pickle) : ')
root = tk.Tk()
root.withdraw()

file_path = filedialog.askdirectory()

if os.path.isdir(file_path):
    print('The folder is a valid folder')
    
    data_name = os.listdir(file_path)
    if len(data_name) == 0:
        print('The folder is empty.')
        quit()
        
else:
    print('not a directory')
    quit()


##########
#Simulation parameters
##########

#Simulation tests
test_deesse = str(input('Do you want to run the deesse simulation ? (True or False) :'))
test_GRF    = str(input('Do you want to run the GRF simulation ? (True or False) :'))
test_krig   = str(input('Do you want to run the Kriging estimation ? (True or False) :'))

#Ouput folder
name_simu_set = str(input('What is the name of the ouput folder to be created ? (simulation_outputxxxx) :'))

#Create the output folder
if test_deesse == 'True'or test_GRF =='True':
    #Nb of simulation
    nbReal = int(input('How many realisation by simulation set ? : '))
    
    #Create the folder for the simulation
    save_path_sim = '../simulation_output'+name_simu_set

    if not(os.path.exists(save_path_sim)):
            os.mkdir(save_path_sim)
    else: 
        for root, dirs, files in os.walk(save_path_sim, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
                
            os.rmdir(save_path_sim)
            os.mkdir(save_path_sim)

    #DeeSse parameters
    para_b = str(input('Do you want to use the deeSse parameters set by default (n=12, t=0.005, f=0.5)? (True or False) : '))

    if para_b == 'False':
        print('Set up the deeSse parameters : ')
        n = int(input('n : '))
        t = float(input('t : '))
        f = float(input('f : '))

    else:
        print('Default parameters are used.')
        n, t, f = 12, 0.005, 0.5
        

##########
#Kriging parameters
##########

                 
if test_krig == 'True':    
    print('The folder for the kriging simulation is "../simulation_output_krig{}". '.format(name_simu_set))
    save_path_kri = '../simulation_output_krig'+name_simu_set

    #Create the folder for the kriging
    if not(os.path.exists(save_path_kri)):
            os.mkdir(save_path_kri)
    else: 
        for root, dirs, files in os.walk(save_path_kri, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
                
            os.rmdir(save_path_kri)
            os.mkdir(save_path_kri)
            
#Kriging and GRF parameters
if test_krig == 'True' or test_GRF == 'True':
    rangeM = int(input('Define the range of the model (default value recommended is 500) : '))
    sillM  = int(input('Define the sill of the model (default value recommended is 1400) : '))
    print('The default model is set to be spherical.')

    cov_model = gcm.CovModel2D(elem=[
    ('spherical', {'w':380., 'r':[324,228]}),
    ('gaussian', {'w':90., 'r':[564,564]}),
    ('gaussian', {'w':130., 'r':[10000,1000]}),
    ('gaussian', {'w':20., 'r':[10000,1800]}),
    ('spherical', {'w':20., 'r':[10000,1000]})# elementary contribution
                       ], alpha=20,  name='model-2D test')
    cov_fun   = cov_model.func()
    vario_fun = cov_model.vario_func()


###########
#Simulation
###########

for name in data_name:
    
    #Load Data
    trueMNT, trend_cut, position, hd_df, ti, mask_box, mask_box_ti = read_data(file_path, name)
    
    #Clear the ti
    ti[ti == np.min(ti) ] = np.nan
    
    #DeeSse run
    if test_deesse == 'True':
        #The whole Ti is used as conditionning data:
        mask_ti = mask_box_ti      #mask of the ti plus the cutted part for the synthetic data
        hd_pts  = create_hd(hd_df) #redefine the coord of the hd in the grid (ox =0, oy=0)
        ti_img  = create_ti(ti)    #redefine the origin of the ti to ox=0, oy=0
        simuMPS = deeSse_run_ti(ti_img, mask_ti, hd_pts, n=n, t=t, f=f, nReal = nbReal)
        extrMPS = extract_simu_zone(simuMPS,position) #extract the simulated zone
    
    else:
        extrMPS = None

    #GRF run
    if test_GRF == 'True':
        X,Y = create_hd_grf(hd_df,position)
        dimension, spacing, origin = create_grid(position)
    
        extensionMin = [grf.extension_min(r, n, s) for r, n, s in zip(cov_model.rxy(), dimension, spacing)]
        simuGRF      = grf.grf2D(cov_fun, dimension, spacing, origin, x=X, v=Y, 
                   extensionMin=extensionMin, nreal=int(nbReal))
    else:
        simuGRF = None
    
    #Save simulation outputs
    if test_deesse == 'True' or test_GRF == 'True':             
            with open(save_path_sim+'/'+name[:-7]+'_simu.pickle','wb') as file:
                pickle.dump([trueMNT, trend_cut, [extrMPS, simuGRF], mask_box_ti, position], file, pickle.HIGHEST_PROTOCOL)

    #Kriging run
    if test_krig == 'True':
        X,Y = create_hd_grf(hd_df,position)
        dimension, spacing, origin = create_grid(position)
    
        extensionMin = [grf.extension_min(r, n, s) for r, n, s in zip(cov_model.rxy(), dimension, spacing)]
        
        std_test=True
        #We recommend to not krig on the whole glacier but use the mean of GRF simulation
        if std_test==True:
            krige, krige_std = grf.krige2D(X, Y, cov_fun, dimension, spacing, origin, extensionMin=extensionMin)
        else:
            krige = grf.krige2D(X, Y, cov_fun, dimension, spacing, origin, extensionMin=extensionMin, computeKrigSD=False)
            krige_std = None
            
        #Save kriging output         
        with open(save_path_kri+'/'+name[:-7]+'_krige.pickle','wb') as file:
            pickle.dump([trueMNT, trend_cut, [krige, krige_std], mask_box_ti, position],file, pickle.HIGHEST_PROTOCOL)

    
    
    
print('------------ \n \n ')
print('Success !')
print('\n \n ------------  ')


######
#old
######
#Simu2 zone + Pyramide
#mask_zone = mask[1]     
#simu4   = deeSse_run_zone(ti_img, mask_zone, hd_pts, n=n, t=t, f=f, nReal = nbReal)
#extr4   = extract_simu_zone(simu4,position)