import numpy

from DataModule import *
import numpy as np
from const import *
import math
import matplotlib.pyplot as plt


def dilatation(land, rows, cols):
    res = np.zeros([rows, cols])
    for latIdx in range(rows-2):
        for lonIdx in range(cols-2):
            i = latIdx + 1
            j = lonIdx + 1
            if land[i, j] or land[i, j-1] or land[i, j+1] or land[i-1, j-1] or land[i-1, j] or land[i-1, j+1] or \
               land[i+1, j-1] or land[i+1, j] or land[i+1, j+1]:
                res[i, j] = 1
    return res


def main():
    print("hey there")
    filePath = './workspace/data/MetO-NWS-WAV-2022-01.nc'
    VSDX = np.array(readData(filePath, 'VSDX'))
    VSDY = np.array(readData(filePath, 'VSDY'))
    lat = np.array(readData(filePath, 'latitude'))
    lon = np.array(readData(filePath, 'longitude'))
    tt = np.array(readData(filePath, 'time'))
    timeResolution = 3600
    northResolution = LAT_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS
    eastResolution = LON_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS * math.cos(lat[0] / 180.0 * math.pi)
    areaUnit = northResolution * eastResolution
    numOfTurbinePerUnit = int(areaUnit / TURBINE_COVER_AREA)
    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    for i in range(len(tt)):
        vx = VSDX[i, :, :]
        vy = VSDY[i, :, :]
        velo = np.sqrt(np.square(vx) + np.square(vy))
        E_velo = 0.5 * SEA_WATER_DENSITY * CROSS_AREA_TURBINE_SMALL * TURBINE_EFFICIENT * np.power(velo, 3) \
                 * numOfTurbinePerUnit
        totalEnergyPerMonth = totalEnergyPerMonth + E_velo
    landMask = np.zeros([len(lat), len(lon)])
    for i in range(len(lat)):
        for j in range(len(lon)):
            if numpy.isnan(VSDX[1, i, j]):
                landMask[i, j] = 1
    originalLandMask = np.copy(landMask)
    # landMask = dilatation(landMask, len(lat), len(lon))
    for i in range(3):
        landMask = dilatation(landMask, len(lat), len(lon))

    totalEnergyPerDay = []
    lon, lat = np.meshgrid(lon, lat)
    # plt.pcolor(lon, lat, totalEnergyPerMonth)
    plt.pcolor(lon, lat, landMask - originalLandMask)
    plt.colorbar()
    plt.show()


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
