# -*- coding: utf-8 -*-
"""
Created on Sat May 20 15:53:05 2023

read nc file and crop data

@author: ADIMATE
"""
# import netCDF4
import numpy as np
import xarray as xr
# import pandas as pd
import matplotlib.pyplot as plt

# import cartopy.crs as ccrs
# import time


# Reading nc files as xarray
DS1 = xr.open_dataset(".//data/MetO-NWS-WAV-hi_1684785430307.nc")
DS2 = xr.open_dataset(".//data/GlobalOcean.nc")
print(DS1)

# Plotting
# for i in range(len(DS1.time)):
#     if i%10==0:
#         plt.figure(1)
#         DS1.VHM0.isel(time=i).plot()
#         plt.show()

t = input("Enter date (yyyy-mm-dd):")
h = input("Enter time 00-23 (hh):")
tt = t + "T" + h + ":00:00"
# tt="2023-04-01T23:30:00"
# t=np.datetime64(tt)


plt.figure(2)
DS2.utotal.sel(time=tt, method="nearest").plot()
plt.show()

# f1 = netCDF4.Dataset('.//data/MetO-NWS-WAV-hi_1684785430307.nc')
# f2 = netCDF4.Dataset('.//data/GlobalOcean.nc')
# #print(f)

# #print(f.variables.keys()) # get all variable names

# SWH = f1.variables['VHM0'] # Significant wave height variable
# VX = f1.variables['VSDX'] # wave stokes drift x velocity variable
# VY = f1.variables['VSDY'] # wave stokes drift y velocity variable
# print(SWH)

# # SWH.dimensions
# # SWH.shape

# tim = f1.variables['time']
# lat,long = f1.variables['latitude'], f1.variables['longitude']

# tm=tim[:]
# lt=lat[:]
# lg=long[:]

# print(tm)