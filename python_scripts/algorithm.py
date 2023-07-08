import copy
import numpy as np
from math import sqrt, cos, pow

from DataModule import *

PI = 3.1415926


def dilatation(land, rows, cols):
    res = np.zeros([rows, cols])
    for latIdx in range(rows - 2):
        for lonIdx in range(cols - 2):
            i = latIdx + 1
            j = lonIdx + 1
            if land[i, j] or land[i, j - 1] or land[i, j + 1] or land[i - 1, j - 1] or land[i - 1, j] or land[
                i - 1, j + 1] or \
                    land[i + 1, j - 1] or land[i + 1, j] or land[i + 1, j + 1]:
                res[i, j] = 1
    return res


def GetLandMask(data, rows, cols, operationCnt):
    landMask = np.zeros([rows, cols])
    for i in range(rows):
        for j in range(cols):
            if np.isnan(data[i, j]):
                landMask[i, j] = 1
    originalLandMask = np.copy(landMask)
    for i in range(operationCnt):
        landMask = dilatation(landMask, rows, cols)
    return originalLandMask, landMask - originalLandMask


def CurrPowerMap(filePath, numOfTurbinePerUnit, const):
    VSDX = np.array(readData(filePath, 'VSDX'))
    VSDY = np.array(readData(filePath, 'VSDY'))
    lat = np.array(readData(filePath, 'latitude'))
    lon = np.array(readData(filePath, 'longitude'))
    tt = np.array(readData(filePath, 'time'))

    deltaT = 1
    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    for i in range(len(tt)):
        vx = VSDX[i, :, :]
        vy = VSDY[i, :, :]
        velo = np.sqrt(np.square(vx) + np.square(vy))
        E_velo = 0.5 * const.SEA_WATER_DENSITY * const.CROSS_AREA_TURBINE_SMALL * const.TURBINE_EFFICIENT * \
                 np.power(velo, 3) * numOfTurbinePerUnit * deltaT
        totalEnergyPerMonth = totalEnergyPerMonth + E_velo
    return totalEnergyPerMonth / len(tt)


def CurrPowerSeries(file, maxIdx, numOfTurbinePerUnit, const):
    VSDX = np.array(readData(file, 'VSDX'))
    VSDY = np.array(readData(file, 'VSDY'))
    tt = np.array(readData(file, 'time'))
    totalEnergyPerDay = 0
    deltaT = 1
    dailyPowerSeq = []
    timeSeq = []
    dayCnt = 1
    for t in range(len(tt)):
        vx = VSDX[t, maxIdx[0], maxIdx[1]]
        vy = VSDY[t, maxIdx[0], maxIdx[1]]
        velo = sqrt(vx ** 2 + vy ** 2)
        E_velo = 0.5 * const.SEA_WATER_DENSITY * const.CROSS_AREA_TURBINE_SMALL * const.TURBINE_EFFICIENT * \
                 pow(velo, 3) * numOfTurbinePerUnit * deltaT
        totalEnergyPerDay = totalEnergyPerDay + E_velo
        if t % 24 == 23:
            timeSeq.append(copy.copy(dayCnt))
            dayCnt = dayCnt + 1
            dailyPowerSeq.append(copy.copy(totalEnergyPerDay / 24))
            totalEnergyPerDay = 0
    return dailyPowerSeq, timeSeq


def WavePotentialMap(filePath, numOfTurbinePerUnit, const):
    VHM = np.array(readData(filePath, 'VHM0'))
    VTM = np.array(readData(filePath, 'VTM02'))
    lat = np.array(readData(filePath, 'latitude'))
    lon = np.array(readData(filePath, 'longitude'))
    tt = np.array(readData(filePath, 'time'))

    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    deltaT = 1
    for i in range(len(tt)):
        Hw = VHM[i, :, :]
        Tw = VTM[i, :, :]
        E = const.SEA_WATER_DENSITY * (const.GRAVITY ** 2) * (
                    Hw ** 2) * Tw * numOfTurbinePerUnit * const.TURBINE_EFFICIENT \
            * const.WIDTH_OF_GENERATOR / 64 / PI * deltaT
        totalEnergyPerMonth = totalEnergyPerMonth + E
    return totalEnergyPerMonth / len(tt)


def WavePotentialSeries(file, maxIdx, numOfTurbinePerUnit, const):
    VHM = np.array(readData(file, 'VHM0'))
    VTM = np.array(readData(file, 'VTM02'))
    tt = np.array(readData(file, 'time'))
    totalEnergyPerDay = 0
    deltaT = 1
    dailyPowerSeq = []
    timeSeq = []
    dayCnt = 1
    for t in range(len(tt)):
        Hw = VHM[t, maxIdx[0], maxIdx[1]]
        Tw = VTM[t, maxIdx[0], maxIdx[1]]
        E = const.SEA_WATER_DENSITY * (const.GRAVITY ** 2) * (
                    Hw ** 2) * Tw * numOfTurbinePerUnit * const.TURBINE_EFFICIENT \
            * const.WIDTH_OF_GENERATOR / 64 / PI * deltaT
        totalEnergyPerDay = totalEnergyPerDay + E
        if t % 24 == 23:
            timeSeq.append(copy.copy(dayCnt))
            dayCnt = dayCnt + 1
            dailyPowerSeq.append(copy.copy(totalEnergyPerDay / 24))
            totalEnergyPerDay = 0
    return dailyPowerSeq, timeSeq


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


def CurrEnergy(fileLists, const):
    tempData = readData(fileLists[0], 'VSDX')
    lat = np.array(readData(fileLists[0], 'latitude'))
    lon = np.array(readData(fileLists[0], 'longitude'))
    northResolution = const.LAT_RESOLUTION / 180.0 * PI * const.EARTH_RADIUS
    eastResolution = const.LON_RESOLUTION / 180.0 * PI * const.EARTH_RADIUS * cos(lat[0] / 180.0 * PI)
    areaUnit = northResolution * eastResolution
    numOfTurbinePerUnit = int(areaUnit / const.TURBINE_COVER_AREA)
    dilatationCnt = int(const.DISTANCE_LIMIT / max(northResolution, eastResolution))

    landMask, searchArea = GetLandMask(tempData[0, :, :], len(lat), len(lon), dilatationCnt)

    currentEnergy = DataStruct()
    currentEnergy.totalPowerMap = np.zeros([len(lat), len(lon)])
    for file in fileLists:
        powerMap = CurrPowerMap(file, 1, const)
        currentEnergy.monPowerMap.append(np.array(powerMap) * 1)
        currentEnergy.totalPowerMap = currentEnergy.totalPowerMap + np.array(powerMap) / len(fileLists)

    maxVal, maxIdx = SearchMaximum(currentEnergy.totalPowerMap, searchArea, len(lat), len(lon))
    currentEnergy.optSite = [maxIdx, [lat[maxIdx[0]], lon[maxIdx[1]]]]

    for file in fileLists:
        timeSeries, timeIdx = CurrPowerSeries(file, currentEnergy.optSite[0], 1, const)
        currentEnergy.timeSeries = currentEnergy.timeSeries + list(timeSeries)
        currentEnergy.timeIdx = currentEnergy.timeIdx + list(np.array(timeIdx) + len(currentEnergy.timeIdx))
    currentEnergy.dailyAvg = np.average(currentEnergy.timeSeries)
    currentEnergy.lat = lat
    currentEnergy.lon = lon

    return currentEnergy


def WaveEnergy(fileLists, const):
    tempData = readData(fileLists[0], 'VSDX')
    lat = np.array(readData(fileLists[0], 'latitude'))
    lon = np.array(readData(fileLists[0], 'longitude'))
    northResolution = const.LAT_RESOLUTION / 180.0 * PI * const.EARTH_RADIUS
    eastResolution = const.LON_RESOLUTION / 180.0 * PI * const.EARTH_RADIUS * cos(lat[0] / 180.0 * PI)
    areaUnit = northResolution * eastResolution
    numOfTurbinePerUnit = int(areaUnit / const.TURBINE_COVER_AREA)
    dilatationCnt = int(const.DISTANCE_LIMIT / max(northResolution, eastResolution))

    landMask, searchArea = GetLandMask(tempData[0, :, :], len(lat), len(lon), dilatationCnt)

    wavePotential = DataStruct()
    wavePotential.totalPowerMap = np.zeros([len(lat), len(lon)])
    for file in fileLists:
        powerMap = WavePotentialMap(file, 1, const)
        wavePotential.monPowerMap.append(np.array(powerMap) * 1)
        wavePotential.totalPowerMap = wavePotential.totalPowerMap + np.array(powerMap) / len(fileLists)

    maxVal, maxIdx = SearchMaximum(wavePotential.totalPowerMap, searchArea, len(lat), len(lon))
    wavePotential.optSite = [maxIdx, [lat[maxIdx[0]], lon[maxIdx[1]]]]

    for file in fileLists:
        timeSeries, timeIdx = WavePotentialSeries(file, wavePotential.optSite[0], 1, const)
        wavePotential.timeSeries = wavePotential.timeSeries + list(timeSeries)
        wavePotential.timeIdx = wavePotential.timeIdx + list(np.array(timeIdx) + len(wavePotential.timeIdx))
    wavePotential.dailyAvg = np.average(wavePotential.timeSeries)
    wavePotential.lat = lat
    wavePotential.lon = lon

    # plt.pcolor(lon, lat, searchArea)
    # plt.colorbar()
    # plt.show()
    # plt.pcolor(lon, lat, landMask+searchArea)
    # plt.colorbar()
    # plt.show()
    return wavePotential


def TidalEnergyMap(file, areaUnit, const):
    SSH = np.array(readData(file, 'zos'))
    lat = np.array(readData(file, 'lat'))
    lon = np.array(readData(file, 'lon'))
    tt = np.array(range(len(readData(file, 'time'))))

    rs = 0
    cs = 0
    # find a pixel which is not nan
    for i in range(len(lat)):
        for j in range(len(lon)):
            if not np.isnan(SSH[0, i, j]):
                rs = i
                cs = j
                break

    # calculate tidal peak time according to the pixel found
    peakIdx = []
    peakVal = []
    for t in range(len(tt) - 2):
        idx = t + 1
        if (SSH[idx, rs, cs] - SSH[idx - 1, rs, cs]) * (SSH[idx + 1, rs, cs] - SSH[idx, rs, cs]) < 0 \
                or SSH[idx, rs, cs] == SSH[idx - 1, rs, cs]:
            peakIdx.append(copy.copy(idx))
            peakVal.append(copy.copy(SSH[idx, rs, cs]))

    # calculate the tidal energy
    totalEnergyPerMonth = np.zeros([len(lat), len(lon)])
    for t in range(len(peakIdx) - 1):
        deltaH = np.abs(SSH[peakIdx[t], :, :] - SSH[peakIdx[t + 1], :, :])
        E = 0.5 * const.SEA_WATER_DENSITY * const.GRAVITY * areaUnit * np.square(deltaH) * const.DAM_EFFICIENT
        totalEnergyPerMonth = totalEnergyPerMonth + E

    # plt.plot(tt/24, SSH[:, rs, cs])
    # plt.scatter(np.array(peakIdx)/24, peakVal)
    # plt.title('SSH in Jan. 2022')
    # plt.xlabel('time [day]')
    # plt.ylabel('height [m]')
    # plt.grid()
    # plt.tight_layout()
    # plt.show()
    return totalEnergyPerMonth / len(tt) / 3600, peakIdx


def TidalEnergySeries(file, maxIdx, peakIdx, areaUnit, const):
    SSH = np.array(readData(file, 'zos'))

    timeSeries = []
    for t in range(len(peakIdx) - 1):
        deltaH = np.abs(SSH[peakIdx[t], maxIdx[0], maxIdx[1]] - SSH[peakIdx[t + 1], maxIdx[0], maxIdx[1]])
        E = 0.5 * const.SEA_WATER_DENSITY * areaUnit * const.GRAVITY * np.square(deltaH) * const.DAM_EFFICIENT
        timeSeries.append(copy.copy(E / (peakIdx[t + 1] - peakIdx[t]) / 3600))
    return timeSeries, peakIdx[1:]


def TidalEnergy(fileLists, const):
    # fileLists = ['./workspace/data/MetO-NWS-PHY-hi-SSH-2022-01.nc', './workspace/data/MetO-NWS-PHY-hi-SSH-2022-02.nc',
    #              './workspace/data/MetO-NWS-PHY-hi-SSH-2022-03.nc']

    # fileLists = ['./workspace/data/MetO-NWS-PHY-hi-SSH-2022-03.nc']
    tempData = readData(fileLists[0], 'zos')
    lat = np.array(readData(fileLists[0], 'lat'))
    lon = np.array(readData(fileLists[0], 'lon'))
    # tt = np.array(readData(fileLists[0], 'time'))
    northResolution = const.LAT_RESOLUTION / 180.0 * PI * const.EARTH_RADIUS
    eastResolution = const.LON_RESOLUTION / 180.0 * PI * const.EARTH_RADIUS * cos(lat[0] / 180.0 * PI)
    areaUnit = northResolution * eastResolution

    landMask, searchArea = GetLandMask(tempData[0, :, :], len(lat), len(lon), 1)

    tidalEnergy = DataStruct()
    tidalEnergy.totalPowerMap = np.zeros([len(lat), len(lon)])
    tidalPeakIdx = []
    for file in fileLists:
        powerMap, peakIdx = TidalEnergyMap(file, 1, const)
        tidalPeakIdx.append(peakIdx.copy())
        tidalEnergy.monPowerMap.append(copy.copy(powerMap))
        tidalEnergy.totalPowerMap = tidalEnergy.totalPowerMap + powerMap / len(fileLists)

    maxVal, maxIdx = SearchMaximum(tidalEnergy.totalPowerMap, searchArea, len(lat), len(lon))
    tidalEnergy.optSite = [maxIdx, [lat[maxIdx[0]], lon[maxIdx[1]]]]

    j = 0
    timeShift = 0
    for file in fileLists:
        timeSeries, timeIdx = TidalEnergySeries(file, maxIdx, tidalPeakIdx[j], 1, const)
        j = j + 1
        tidalEnergy.timeSeries = tidalEnergy.timeSeries + list(timeSeries)
        tidalEnergy.timeIdx = tidalEnergy.timeIdx + list(np.array(timeIdx) / 24 + timeShift)
        timeShift = timeShift + len(readData(file, 'time')) / 24
    # tidalEnergy.dailyAvg = tidalEnergy.totalPowerMap[maxIdx[0], maxIdx[1]] / timeShift
    tidalEnergy.dailyAvg = np.average(tidalEnergy.timeSeries)
    tidalEnergy.lat = lat
    tidalEnergy.lon = lon
    return tidalEnergy

# if __name__ == "__main__":
#     filenames = [[], []]
#     dataPath = './workspace/data/'
#     fileList = os.walk(dataPath)
#     for root, dir, fileList in fileList:
#         for file in fileList:
#             if not file.find("WAV") == -1:
#                 filenames[0].append(dataPath + file)
#             if not file.find("SSH") == -1:
#                 filenames[1].append(dataPath + file)
#     CurrWaveEnergy(filenames[0])
#     TidalEnergy(filenames[1])
