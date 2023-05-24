# -*- coding: utf-8 -*-
"""
Created on Sat May 20 15:53:05 2023

read nc file and crop data

@author: Adil Wankhede
"""
import netCDF4
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import time

f1 = netCDF4.Dataset('.//data/MetO-NWS-WAV-hi_1684785430307.nc')
f2 = netCDF4.Dataset('.//data/GlobalOcean.nc')
# print(f)

# print(f.variables.keys()) # get all variable names

SWH = f1.variables['VHM0']  # Significant wave height variable
VX = f1.variables['VSDX']  # wave stokes drift x velocity variable
VY = f1.variables['VSDY']  # wave stokes drift y velocity variable
print(SWH)

# SWH.dimensions
# SWH.shape

tim = f1.variables['time']
lat, long = f1.variables['latitude'], f1.variables['longitude']

tm = tim[:]
lt = lat[:]
lg = long[:]

# print(tm)

DS1 = xr.open_dataset(".//data/MetO-NWS-WAV-hi_1684785430307.nc")
DS2 = xr.open_dataset(".//data/GlobalOcean.nc")
print(DS1)

plt.figure(1)
DS1.VHM0.isel(time=720).plot()
plt.show()

plt.figure(2)
DS2.uo.isel(time=0).plot()
plt.show()

# Plot a 2D map for 21st April 2023

# fig1=DS.VSDX.isel(time=500).plot()
# fig2=DS.VSDY.isel(time=500).plot()
# for i in range(len(tm)):
#     plt.figure()
#     DS.VHM0.isel(time=i).plot()

#     time.sleep(0.5) # Sleep for 0.5 seconds


