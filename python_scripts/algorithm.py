import numpy
import copy
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


def GetLandMask(data, rows, cols):
    landMask = np.zeros([rows, cols])
    for i in range(rows):
        for j in range(cols):
            if numpy.isnan(data[i, j]):
                landMask[i, j] = 1
    originalLandMask = np.copy(landMask)
    # landMask = dilatation(landMask, len(lat), len(lon))
    for i in range(3):
        landMask = dilatation(landMask, rows, cols)
    return originalLandMask, landMask-originalLandMask


def CurrEnergyMap(filePath, numOfTurbinePerUnit):
    VSDX = np.array(readData(filePath, 'VSDX'))
    VSDY = np.array(readData(filePath, 'VSDY'))
    lat = np.array(readData(filePath, 'latitude'))
    lon = np.array(readData(filePath, 'longitude'))
    tt = np.array(readData(filePath, 'time'))

    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    for i in range(len(tt)):
        vx = VSDX[i, :, :]
        vy = VSDY[i, :, :]
        velo = np.sqrt(np.square(vx) + np.square(vy))
        E_velo = 0.5 * SEA_WATER_DENSITY * CROSS_AREA_TURBINE_SMALL * TURBINE_EFFICIENT * np.power(velo, 3) \
            * numOfTurbinePerUnit * (TIME_RESOLUTION / KWH_TO_J)
        totalEnergyPerMonth = totalEnergyPerMonth + E_velo
    return totalEnergyPerMonth


def CurrEnergySeries(file, maxIdx, numOfTurbinePerUnit):
    VSDX = np.array(readData(file, 'VSDX'))
    VSDY = np.array(readData(file, 'VSDY'))
    tt = np.array(readData(file, 'time'))
    totalEnergyPerDay = 0
    dailyEnergySeq = []
    timeSeq = []
    dayCnt = 1
    for t in range(len(tt)):
        vx = VSDX[t, maxIdx[0], maxIdx[1]]
        vy = VSDY[t, maxIdx[0], maxIdx[1]]
        velo = math.sqrt(vx ** 2 + vy ** 2)
        E_velo = 0.5 * SEA_WATER_DENSITY * CROSS_AREA_TURBINE_SMALL * TURBINE_EFFICIENT * math.pow(velo, 3) \
            * numOfTurbinePerUnit * (TIME_RESOLUTION / KWH_TO_J)
        totalEnergyPerDay = totalEnergyPerDay + E_velo
        if t % 24 == 23:
            timeSeq.append(copy.copy(dayCnt))
            dayCnt = dayCnt + 1
            dailyEnergySeq.append(copy.copy(totalEnergyPerDay))
            totalEnergyPerDay = 0
    return dailyEnergySeq


def WavePotentialMap(filePath, numOfTurbinePerUnit):
    VHM = np.array(readData(filePath, 'VHM0'))
    VTM = np.array(readData(filePath, 'VTM02'))
    lat = np.array(readData(filePath, 'latitude'))
    lon = np.array(readData(filePath, 'longitude'))
    tt = np.array(readData(filePath, 'time'))

    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    for i in range(len(tt)):
        Hw = VHM[i, :, :]
        Tw = VTM[i, :, :]
        E_velo = SEA_WATER_DENSITY * (GRAVITY**2) * (Hw**2) * Tw * CROSS_AREA_TURBINE_SMALL * numOfTurbinePerUnit \
            / 64 / math.pi * (TIME_RESOLUTION / KWH_TO_J)
        totalEnergyPerMonth = totalEnergyPerMonth + E_velo
    return totalEnergyPerMonth


def WavePotentialSeries(file, maxIdx, numOfTurbinePerUnit):
    VHM = np.array(readData(file, 'VHM0'))
    VTM = np.array(readData(file, 'VTM02'))
    tt = np.array(readData(file, 'time'))
    totalEnergyPerDay = 0
    dailyEnergySeq = []
    timeSeq = []
    dayCnt = 1
    for t in range(len(tt)):
        Hw = VHM[t, maxIdx[0], maxIdx[1]]
        Tw = VTM[t, maxIdx[0], maxIdx[1]]
        E_velo = SEA_WATER_DENSITY * (GRAVITY**2) * (Hw**2) * Tw * CROSS_AREA_TURBINE_SMALL * numOfTurbinePerUnit \
            / 64 / math.pi * (TIME_RESOLUTION / KWH_TO_J)
        totalEnergyPerDay = totalEnergyPerDay + E_velo
        if t % 24 == 23:
            timeSeq.append(copy.copy(dayCnt))
            dayCnt = dayCnt + 1
            dailyEnergySeq.append(copy.copy(totalEnergyPerDay))
            totalEnergyPerDay = 0
    return dailyEnergySeq


def SearchMaximum(energyMap, searchArea, rows, cols):
    maxVal = 0
    maxIdx = []
    for i in range(rows):
        for j in range(cols):
            if searchArea[i][j]:
                if energyMap[i][j] > maxVal:
                    maxVal = energyMap[i][j]
                    maxIdx = [i, j]
    return maxVal, maxIdx


def main():
    # fileLists = ['./workspace/data/MetO-NWS-WAV-2022-01.nc', './workspace/data/MetO-NWS-WAV-2022-02.nc',
    #              './workspace/data/MetO-NWS-WAV-2022-03.nc']
    fileLists = ['./workspace/data/MetO-NWS-WAV-2022-01.nc']
    tempData = readData(fileLists[0], 'VSDX')
    lat = np.array(readData(fileLists[0], 'latitude'))
    lon = np.array(readData(fileLists[0], 'longitude'))
    northResolution = LAT_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS
    eastResolution = LON_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS * math.cos(lat[0] / 180.0 * math.pi)
    areaUnit = northResolution * eastResolution
    numOfTurbinePerUnit = int(areaUnit / TURBINE_COVER_AREA)

    landMask, searchArea = GetLandMask(tempData[0, :, :], len(lat), len(lon))

    currentEnergy = DataStruct()
    wavePotential = DataStruct()
    wavePotential.totalEnergyMap = np.zeros([len(lat), len(lon)])
    currentEnergy.totalEnergyMap = np.zeros([len(lat), len(lon)])
    for file in fileLists:
        energyMap = CurrEnergyMap(file, numOfTurbinePerUnit)
        currentEnergy.monEnergyMap.append(copy.copy(energyMap))
        currentEnergy.totalEnergyMap = currentEnergy.totalEnergyMap + energyMap
        energyMap = WavePotentialMap(file, numOfTurbinePerUnit)
        wavePotential.monEnergyMap.append(copy.copy(energyMap))
        wavePotential.totalEnergyMap = wavePotential.totalEnergyMap + energyMap

    maxVal, maxIdx = SearchMaximum(currentEnergy.totalEnergyMap, searchArea, len(lat), len(lon))
    latMax = lat[maxIdx[0]]
    lonMax = lon[maxIdx[1]]
    currentEnergy.optSite = [maxIdx, [latMax, lonMax]]

    maxVal, maxIdx = SearchMaximum(wavePotential.totalEnergyMap, searchArea, len(lat), len(lon))
    latMax = lat[maxIdx[0]]
    lonMax = lon[maxIdx[1]]
    wavePotential.optSite = [maxIdx, [latMax, lonMax]]

    print('max energy output per unit: ' + str(maxVal))
    print('site position: [' + str(lonMax) + ', ' + str(latMax) + ']')

    for file in fileLists:
        currentEnergy.timeSeries = currentEnergy.timeSeries + list(CurrEnergySeries(file, currentEnergy.optSite[0],
                                                                                    numOfTurbinePerUnit))
    currentEnergy.dailyAvg = np.average(currentEnergy.timeSeries)

    for file in fileLists:
        wavePotential.timeSeries = wavePotential.timeSeries + list(WavePotentialSeries(file, wavePotential.optSite[0],
                                                                                       numOfTurbinePerUnit))
    print('average energy per day: ' + str(np.average(wavePotential.timeSeries)))
    wavePotential.dailyAvg = np.average(wavePotential.timeSeries)

    # plot
    lon, lat = np.meshgrid(lon, lat)
    plt.pcolor(lon, lat, wavePotential.totalEnergyMap)
    # plt.pcolor(lon, lat, landMask - originalLandMask)
    plt.colorbar()
    plt.scatter(lonMax, latMax, marker='^')
    plt.show()
    plt.plot(wavePotential.timeSeries, marker='.')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
