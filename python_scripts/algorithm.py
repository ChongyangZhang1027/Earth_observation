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


def GetLandMask(data, rows, cols, operationCnt):
    landMask = np.zeros([rows, cols])
    for i in range(rows):
        for j in range(cols):
            if numpy.isnan(data[i, j]):
                landMask[i, j] = 1
    originalLandMask = np.copy(landMask)
    # landMask = dilatation(landMask, len(lat), len(lon))
    for i in range(operationCnt):
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
    return dailyEnergySeq, timeSeq


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
        E = SEA_WATER_DENSITY * (GRAVITY**2) * (Hw**2) * Tw * numOfTurbinePerUnit * TURBINE_EFFICIENT \
            * WIDTH_OF_GENERATOR / 64 / math.pi * (TIME_RESOLUTION / Tw / KWH_TO_J)
        totalEnergyPerMonth = totalEnergyPerMonth + E
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
        E = SEA_WATER_DENSITY * (GRAVITY**2) * (Hw**2) * Tw * numOfTurbinePerUnit * TURBINE_EFFICIENT \
            * WIDTH_OF_GENERATOR / 64 / math.pi * (TIME_RESOLUTION / Tw / KWH_TO_J)
        totalEnergyPerDay = totalEnergyPerDay + E
        if t % 24 == 23:
            timeSeq.append(copy.copy(dayCnt))
            dayCnt = dayCnt + 1
            dailyEnergySeq.append(copy.copy(totalEnergyPerDay))
            totalEnergyPerDay = 0
    return dailyEnergySeq, timeSeq


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
    fileLists = ['./workspace/data/MetO-NWS-WAV-2022-01.nc', './workspace/data/MetO-NWS-WAV-2022-02.nc',
                 './workspace/data/MetO-NWS-WAV-2022-03.nc']
    # fileLists = ['./workspace/data/MetO-NWS-WAV-2022-01.nc']
    tempData = readData(fileLists[0], 'VSDX')
    lat = np.array(readData(fileLists[0], 'latitude'))
    lon = np.array(readData(fileLists[0], 'longitude'))
    northResolution = LAT_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS
    eastResolution = LON_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS * math.cos(lat[0] / 180.0 * math.pi)
    areaUnit = northResolution * eastResolution
    numOfTurbinePerUnit = int(areaUnit / TURBINE_COVER_AREA)

    landMask, searchArea = GetLandMask(tempData[0, :, :], len(lat), len(lon), 2)

    currentEnergy = DataStruct()
    wavePotential = DataStruct()
    wavePotential.totalEnergyMap = np.zeros([len(lat), len(lon)])
    currentEnergy.totalEnergyMap = np.zeros([len(lat), len(lon)])
    for file in fileLists:
        energyMap = CurrEnergyMap(file, 1)
        currentEnergy.monEnergyMap.append(copy.copy(energyMap))
        currentEnergy.totalEnergyMap = currentEnergy.totalEnergyMap + energyMap
        energyMap = WavePotentialMap(file, 1)
        wavePotential.monEnergyMap.append(copy.copy(energyMap))
        wavePotential.totalEnergyMap = wavePotential.totalEnergyMap + energyMap

    maxVal, maxIdx = SearchMaximum(currentEnergy.totalEnergyMap, searchArea, len(lat), len(lon))
    latMax = lat[maxIdx[0]]
    lonMax = lon[maxIdx[1]]
    currentEnergy.optSite = [maxIdx, [latMax, lonMax]]
    print('max energy output per unit: ' + str(maxVal))
    print('site position: [' + str(lonMax) + ', ' + str(latMax) + ']')

    maxVal, maxIdx = SearchMaximum(wavePotential.totalEnergyMap, searchArea, len(lat), len(lon))
    latMax = lat[maxIdx[0]]
    lonMax = lon[maxIdx[1]]
    wavePotential.optSite = [maxIdx, [latMax, lonMax]]

    for file in fileLists:
        timeSeries, timeIdx = CurrEnergySeries(file, currentEnergy.optSite[0], 1)
        currentEnergy.timeSeries = currentEnergy.timeSeries + list(timeSeries)
        currentEnergy.timeIdx = currentEnergy.timeIdx + list(np.array(timeIdx) + len(currentEnergy.timeIdx))
    currentEnergy.dailyAvg = np.average(currentEnergy.timeSeries)
    print('average energy per day: ' + str(np.average(currentEnergy.timeSeries)))

    for file in fileLists:
        timeSeries, timeIdx = WavePotentialSeries(file, wavePotential.optSite[0], 1)
        wavePotential.timeSeries = wavePotential.timeSeries + list(timeSeries)
        wavePotential.timeIdx = wavePotential.timeIdx + list(np.array(timeIdx) + len(wavePotential.timeIdx))
    wavePotential.dailyAvg = np.average(wavePotential.timeSeries)

    # plot
    lon, lat = np.meshgrid(lon, lat)
    plt.pcolor(lon, lat, currentEnergy.totalEnergyMap)
    plt.colorbar()
    plt.scatter(lonMax, latMax, marker='^')
    plt.title('Current energy distribution map')
    plt.xlabel('lat [deg]')
    plt.ylabel('lon [deg]')
    plt.show()
    plt.plot(currentEnergy.timeIdx, currentEnergy.timeSeries, marker='.')
    plt.title('Daily current energy time series')
    plt.xlabel('time [day]')
    plt.ylabel('power [kWh]')
    plt.grid()
    plt.show()

    # plt.pcolor(lon, lat, searchArea)
    # plt.colorbar()
    # plt.show()
    plt.pcolor(lon, lat, landMask+searchArea)
    plt.colorbar()
    plt.show()


def TidalEnergyMap(file, areaUnit):
    SSH = np.array(readData(file, 'zos'))
    lat = np.array(readData(file, 'lat'))
    lon = np.array(readData(file, 'lon'))
    tt = np.array(range(len(readData(file, 'time'))))

    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    rs = 0
    cs = 0
    for i in range(len(lat)):
        for j in range(len(lon)):
            if not np.isnan(SSH[0, i, j]):
                rs = i
                cs = j
                break

    peakIdx = []
    peakVal = []
    for t in range(len(tt)-2):
        idx = t+1
        if (SSH[idx, rs, cs] - SSH[idx-1, rs, cs]) * (SSH[idx+1, rs, cs] - SSH[idx, rs, cs]) < 0 \
                or SSH[idx, rs, cs] == SSH[idx-1, rs, cs]:
            peakIdx.append(copy.copy(idx))
            peakVal.append(copy.copy(SSH[idx, rs, cs]))
    for t in range(len(peakIdx)-1):
        deltaH = np.abs(SSH[peakIdx[t], :, :] - SSH[peakIdx[t+1], :, :])
        E = 0.5 * SEA_WATER_DENSITY * areaUnit * np.square(deltaH) * TURBINE_EFFICIENT
        totalEnergyPerMonth = totalEnergyPerMonth + E

    # plt.plot(tt/24, SSH[:, rs, cs])
    # plt.scatter(np.array(peakIdx)/24, peakVal)
    # plt.title('SSH in Jan. 2022')
    # plt.xlabel('time [day]')
    # plt.ylabel('height [m]')
    # plt.grid()
    # plt.tight_layout()
    # plt.show()
    return totalEnergyPerMonth, peakIdx


def TidalEnergySeries(file, maxIdx, peakIdx, areaUnit):
    SSH = np.array(readData(file, 'zos'))

    timeSeries = []
    for t in range(len(peakIdx) - 1):
        deltaH = np.abs(SSH[peakIdx[t], maxIdx[0], maxIdx[1]] - SSH[peakIdx[t+1], maxIdx[0], maxIdx[1]])
        E = 0.5 * SEA_WATER_DENSITY * areaUnit * np.square(deltaH) * TURBINE_EFFICIENT
        timeSeries.append(copy.copy(E))
    return timeSeries, peakIdx[1:]


def TidalEnergy():
    fileLists = ['./workspace/data/MetO-NWS-PHY-hi-SSH-2022-01.nc', './workspace/data/MetO-NWS-PHY-hi-SSH-2022-02.nc',
                 './workspace/data/MetO-NWS-PHY-hi-SSH-2022-03.nc']

    # fileLists = ['./workspace/data/MetO-NWS-PHY-hi-SSH-2022-03.nc']
    tempData = readData(fileLists[0], 'zos')
    lat = np.array(readData(fileLists[0], 'lat'))
    lon = np.array(readData(fileLists[0], 'lon'))
    tt = np.array(readData(fileLists[0], 'time'))
    northResolution = LAT_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS
    eastResolution = LON_RESOLUTION / 180.0 * math.pi * EARTH_RADIUS * math.cos(lat[0] / 180.0 * math.pi)
    areaUnit = northResolution * eastResolution

    landMask, searchArea = GetLandMask(tempData[0, :, :], len(lat), len(lon), 1)

    tidalEnergy = DataStruct()
    tidalEnergy.totalEnergyMap = np.zeros([len(lat), len(lon)])
    tidalPeakIdx = []
    for file in fileLists:
        energyMap, peakIdx = TidalEnergyMap(file, 1)
        tidalPeakIdx.append(peakIdx.copy())
        tidalEnergy.monEnergyMap.append(copy.copy(energyMap))
        tidalEnergy.totalEnergyMap = tidalEnergy.totalEnergyMap + energyMap

    maxVal, maxIdx = SearchMaximum(tidalEnergy.totalEnergyMap, searchArea, len(lat), len(lon))
    latMax = lat[maxIdx[0]]
    lonMax = lon[maxIdx[1]]
    tidalEnergy.optSite = [maxIdx, [latMax, lonMax]]

    print('max energy output per unit: ' + str(maxVal))
    print('site position: [' + str(lonMax) + ', ' + str(latMax) + ']')

    j = 0
    timeShift = 0
    for file in fileLists:
        timeSeries, timeIdx = TidalEnergySeries(file, maxIdx, tidalPeakIdx[j], 1)
        j = j + 1
        tidalEnergy.timeSeries = tidalEnergy.timeSeries + list(timeSeries)
        tidalEnergy.timeIdx = tidalEnergy.timeIdx + list(np.array(timeIdx)/24 + timeShift)
        timeShift = timeShift + len(readData(file, 'time')) / 24
    tidalEnergy.dailyAvg = tidalEnergy.totalEnergyMap[maxIdx[0], maxIdx[1]] / timeShift
    print('average energy per day: ' + str(np.average(tidalEnergy.timeSeries)))

    # plot
    lon, lat = np.meshgrid(lon, lat)
    plt.pcolor(lon, lat, tidalEnergy.totalEnergyMap)
    plt.title('Tidal energy distribution map')
    plt.xlabel('lat [deg]')
    plt.ylabel('lon [deg]')
    # plt.pcolor(lon, lat, searchArea)
    plt.colorbar()
    plt.scatter(lonMax, latMax, marker='^')
    plt.show()
    plt.plot(tidalEnergy.timeIdx, tidalEnergy.timeSeries, marker='.')
    plt.title('Daily tidal energy time series')
    plt.xlabel('time [day]')
    plt.ylabel('power [kWh]')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
    # TidalEnergy()
