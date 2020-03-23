#!/usr/bin/env python
# coding: utf-8
#Valentin Dallalba 01/2020

import pickle
import numpy as np
import pandas as pd
from geone import img
import geone.imgplot as imgplt
import geone.customcolors as ccol
import geone.deesseinterface as dsi
import geone.covModel as gcm
import geone.customcolors as ccol

##########
##########

def read_data(path, name):
    '''
    Read the synthetic data picke files.
    Path : path toward the pickle repository.
    Name : pickle file.
    '''
    
    with open(path+'/'+ name,'rb') as file:
        data = pickle.load(file)
    
    return data 


##########
##########

def pandasToPointSet(df):
    """
    Convert pandas DataFrame into a PointSet object
    :param df: (pandas.DataFrame) data frame to be converted
    :return: PointSet:
    A PointSet object
    """
    
    return img.PointSet(npt=len(df),
            nv=len(df.columns),
            val=df.values.transpose(),
            varname=list(df.columns))


##########
##########

def pointSetToPandas(point_set):
    """
    Convert PointSet object into pandas DataFrame

    :param point_set: (PointSet) PointSet to be converted

    :return: pd.DataFrame:
                       A pandas DataFrame
    """
    
    return pd.DataFrame(point_set.val.transpose(), columns=point_set.varname)


##########
##########

def create_hd(hd_df,sx=1,sy=1):
    '''
    Create hd point set based on pandas dataFrame.
    df : dataFrame.
    '''
    
    hd = hd_df.copy()
    hd = hd.drop(['X','Y'],axis='columns')              #drop the columns
    hd = hd.rename(columns={'cell_x':'X','cell_y':'Y'}) #rename the columns
    hd['X'] = hd['X']*sx
    hd['Y'] = hd['Y']*sy
    
    hd['Z'] = 0.5                         #create the Z infos
    hd      = hd[['X','Y','Z','alt']]  #reorganise the columns
    hd_pts  = pandasToPointSet(hd) #create the point set
    
    return hd_pts


##########
##########

def create_ti(ti_arr, sx=1, sy=1, sz=1):
    '''
    Create the TI for the MPS simulation, the ti is the full Ti minus the extracted zone.
    ti : np array.
    '''
    
    shape  = ti_arr.shape
    ti = np.copy(ti_arr)
    ti[ti<-1] = np.nan #float(np.nan)

    ti     = ti[np.newaxis,np.newaxis,:,:]

    ti_Img = img.Img( nx=int(shape[1]), ny=int(shape[0]), nz=1,     
                      sx=sx, sy=sy, sz=sz,
                      ox=0.0, oy=0.0, oz=0.0,
                      nv=1, val=ti.astype('float64'), varname=['alt']
            )
    
    return ti_Img


####################
#DeeSse
####################

def deeSse_run_ti(ti_Img, mask_ti, hd_pts, n=12, t=0.05, f=0.50, nReal=1):
    '''
    DeeSse run, where the simulation use the TI as conditionning data.
    Simulation with pyramides.
    The MPS simulation complete the missing part of the TI.
    ti_Img : Img format, the ti with the exctracted zone remove.
    mask_ti : Img format, the mask that take in the whole TI.
    hd_pts  : pointSet format, the fictives point Set.
    '''
    
    hdpt2        = img.imageToPointSet(ti_Img) #to pass the ti as conditionnig data
    pyrGenParams = dsi.PyramidGeneralParameters(npyramidLevel=2, kx=[2, 2], ky=[2, 2], kz=[0, 0])
    pyrParams    = dsi.PyramidParameters(nlevel=2, pyramidType='continuous')
    
    deesse_input =   dsi.DeesseInput(
    nx=ti_Img.nx, ny=ti_Img.ny, nz=ti_Img.nz,     # dimension of the simulation grid (number of cells)
    sx=ti_Img.sx, sy=ti_Img.sy, sz=ti_Img.sz,     # cells units in the simulation grid (here are the default values)
    ox=ti_Img.ox, oy=ti_Img.oy, oz=ti_Img.oz,     # origin of the simulation grid (here are the default values)
    nv=1, varname='alt',                  # number of variable(s), name of the variable(s)
    nTI=1, TI=ti_Img,                     # number of TI(s), TI (class dsi.Img)
    mask=mask_ti,                 # mask value
    dataPointSet=[hd_pts,hdpt2],      # hard data
    relativeDistanceFlag=True,
    distanceType=1,           # distance type: proportion of mismatching nodes (categorical var., default)
    nneighboringNode=n,       # max. number of neighbors (for the patterns)
    distanceThreshold=t,      # acceptation threshold (for distance between patterns)
    maxScanFraction=f,        # max. scanned fraction of the TI (for simulation of each cell)
        
    pyramidGeneralParameters=pyrGenParams, # pyramid general parameters
    pyramidParameters=pyrParams,           # pyramid parameters for each variable
        
    npostProcessingPathMax=1, # number of post-processing path(s)
    seed=444,                 # seed (initialization of the random number generator)
    nrealization=nReal) 
    
    deesse_output = dsi.deesseRun(deesse_input)
    sim = deesse_output['sim']
    
    return sim


##########
##########

def deeSse_run_zone(ti_Img, mask_zone, hd_pts, n=12, t=0.05, f=0.50, nReal=1):
    '''
    DeeSse run, where the simulation use the TI as conditionning data.
    Simulation with pyramides.
    The MPS simulation complete the missing part of the TI.
    ti_Img : Img format, the ti with the extracted zone remove.
    mask_zone : Img format, the mask that take only the extracted zone.
    hd_pts  : pointSet format, the fictives point Set.
    '''
    
    pyrGenParams = dsi.PyramidGeneralParameters(npyramidLevel=2, kx=[2, 2], ky=[2, 2], kz=[0, 0])
    pyrParams    = dsi.PyramidParameters(nlevel=2, pyramidType='continuous')
    
    deesse_input =   dsi.DeesseInput(
    nx=ti_Img.nx, ny=ti_Img.ny, nz=ti_Img.nz,     # dimension of the simulation grid (number of cells)
    sx=ti_Img.sx, sy=ti_Img.sy, sz=ti_Img.sz,     # cells units in the simulation grid (here are the default values)
    ox=ti_Img.ox, oy=ti_Img.oy, oz=ti_Img.oz,     # origin of the simulation grid (here are the default values)
    nv=1, varname='alt',                  # number of variable(s), name of the variable(s)
    nTI=1, TI=ti_Img,                     # number of TI(s), TI (class dsi.Img)
    mask=mask_zone,           # mask value
    dataPointSet=[hd_pts],        # hard data
    relativeDistanceFlag=True,
    distanceType=1,           # distance type: proportion of mismatching nodes (categorical var., default)
    nneighboringNode=n,       # max. number of neighbors (for the patterns)
    distanceThreshold=t,      # acceptation threshold (for distance between patterns)
    maxScanFraction=f,        # max. scanned fraction of the TI (for simulation of each cell)
    
    pyramidGeneralParameters=pyrGenParams, # pyramid general parameters
    pyramidParameters=pyrParams,           # pyramid parameters for each variable
        
    npostProcessingPathMax=1, # number of post-processing path(s)
    seed=444,                 # seed (initialization of the random number generator)
    nrealization=nReal) 
    
    deesse_output = dsi.deesseRun(deesse_input)
    sim = deesse_output['sim']
    
    return sim


####################
#GRF
####################

def create_hd_grf(hd_df, position):
    hd_df = hd_df.sample(frac=1)
    
    hd_df = hd_df[hd_df['cell_x']!=position[1]]
    hd_df = hd_df[hd_df['cell_y']!=position[3]]
    
    X = np.array([[float(x),float(y)] for x,y in zip(hd_df['cell_x'],hd_df['cell_y'])])
    Y = np.array(hd_df['alt'])
    
    X,Y = remove_duplicate(X,Y)
    return X,Y


##########
##########

def create_grid(position):
    nx,ny = int(position[1]-position[0]), int(position[3]-position[2])
    sx,sy = 1.0, 1.0
    ox,oy = float(position[0]), float(position[2])
    
    dimension = [nx,ny]
    spacing   = [sx,sy]
    origin    = [ox,oy]
    
    return dimension, spacing, origin


##########
##########

def remove_duplicate(X,Y): 
    X, position = np.unique(X,axis=0,return_index=True)
    Y = Y[position]

    return X,Y


##########
##########

def extract_simu_zone(simus,position):
    '''
    Extract the simulated zone.
    Simu : list of realization.
    position : position of the zone to be extracted.
    '''
    extZones = []
    ny = simus[0].ny
    
    for simu in simus:
        zone = simu.val[0,0,position[2]:position[3], position[0]:position[1]]
        extZones.append(zone)
    
    return extZones











