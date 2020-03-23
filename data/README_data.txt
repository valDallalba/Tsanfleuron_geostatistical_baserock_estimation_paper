Data Report : Generated 09.12.19, Modified 24.02.2020
Alexis Neven

-------------------------------Folder DEM--------------------------------------
The folder /pickle and the folder /gslib contain the same data in two different formats:

dsm_alt3D_2m

Alti3D altitude data, organised in an ascii raster. 
Zone covered : the glacier and the area around. 
Resolution : 2m/Pixel
Comments : none

-------------------------------Folder MASKS--------------------------------------
The folder /pickle and the folder /tif contain the same data in two different formats, the pickle files are Geone Img objects, the tif files are raster like objects :

glacier_Mask_2m

Mask covering the Tsanfleuron and Sex Rouge glacier, organised in an ascii raster. The glacier pixel is a 1, when the non-glacier pixel is a 0. 
Zone covered : the glacier and close surrondings. 
Resolution : 2m/Pixel
Comments : none

-------------------------------Folder PointSet--------------------------------------
The folder /pickle and the folder /csv contain the same data in two different formats, the pickle files are Geone PointSet objects, the csv files are the positions and values of the GPR data :

bedRock_GPR

Dataset containing the picking result from the GPR data. The data order is the follwoing : (1) X (2) Y (3) Z (4) time (ns) (5) Depth (m) (6) Bedrock Altitude
Zone covered : the glacier. 
Resolution : Variable
Comments : none

bedRock_MNT.csv

Dataset containing the altitude data of the points around the glacier. This is the altitude of the bedrock where the glacier limits are. The data order is the follwoing : (1) X (2) Y (3) Bedrock Altitude
Zone covered : limit of the glacier. 
Resolution : Variable
Comments : none

-------------------------------Folder TI--------------------------------------
The folder /pickle and the folder /tif contain the same data in two different formats, the pickle files are Geone Img objects, the tif files are raster like objects :

ti_alti1_2016_2m

Training image. DEM from Alti3D cropped to cover the exposed glacial bedrock. Alternative 1 (only close surrundings of the glacier) 
Zone covered : close surronding, exposed bedrock. 
Resolution : 2m/Pixel
Comments : none


ti_alti2_2016_2m

Training image. DEM from Alti3D cropped to cover the exposed glacial bedrock. Alternative 2 (wide surrundings of the glacier) 
Zone covered : wide surronding, exposed bedrock. 
Resolution : 2m/Pixel
Comments : none
