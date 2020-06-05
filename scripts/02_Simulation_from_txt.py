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

exec(open('../functions/02_simulation_functions.py').read())
exec(open('../functions/02_kriging_functions.py').read())


#######
#Load Genereted Data
#######

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
    
#######
#Load simulation paramters
#######
    
print('Select the folder that contain the simulation parameters (text file) : ')
root = tk.Tk()
root.withdraw()

txt_path = filedialog.askopenfiles()

if os.path.isfile(str(txt_path[0].name)):
    print('The text file is valid.')
    path_txt = txt_path[0].name
    
else:
    print('not a text file.')
    quit()

with open(path_txt, 'r') as file:
    lines = file.readlines()
    lines = lines[1:]

parameters_set = []
for line in lines:
    parameters_set.append(line.strip().split(','))
    
start = time.time()    
##########    
#Run the simulation
##########

for i, parameters in enumerate(parameters_set):
    simulation(file_path, data_name, parameters, i)
    print('Set {} is done !! /n'.format(i))
    
stop = time.time()
timeRun = stop-start
print('Simulation time is : {}s.\n'.format(timeRun))
print('All the simulation set are done !!!!')
