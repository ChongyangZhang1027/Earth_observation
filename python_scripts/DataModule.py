import xarray as xr
import netCDF4 as nc
import numpy as np
from const import constNum


class DataStruct:
    def __init__(self):
        self.monPowerMap = []  # monthly distribution map for three kinds of energy
        self.totalPowerMap = []
        self.timeSeries = []  # daily time series for three kinds of energy
        self.timeIdx = []
        self.optSite = []
        self.dailyAvg = 0
        self.lat = []
        self.lon = []

    def _dataClear(self):
        self.monPowerMap = []
        self.totalPowerMap = []
        self.timeSeries = []


def readData(filePath, param):
    data_set = xr.open_dataset(filePath)
    data = data_set[param]
    return data


def strAddZero(timeStr):
    if len(timeStr) < 2:
        timeStr = '0' + timeStr
    return timeStr


def saveData(path, oceanEnergy):
    text = ["tidal", "wave", "current"]
    unit = ["W/m^2", "kW/m", "W/m^2"]
    for i in range(3):
        data = nc.Dataset(path + text[i] + '.nc', 'w', format='NETCDF4')

        # --创建维度，第一个参数为维度名，第二个参数为维度长度--#
        data.createDimension('lat', len(oceanEnergy[i].lat))
        data.createDimension('lon', len(oceanEnergy[i].lon))
        data.createDimension('mon', len(oceanEnergy[i].monPowerMap))
        data.createDimension('time', len(oceanEnergy[i].timeSeries))

        data.createVariable('lat', np.float32, 'lat', fill_value=0)
        data.variables['lat'][:] = np.array(oceanEnergy[i].lat)
        # data.variables['lat'].lat = 'deg'

        data.createVariable('lon', np.float32, 'lon', fill_value=0)
        data.variables['lon'][:] = np.array(oceanEnergy[i].lon)
        # data.variables['lon'].lon = 'deg'

        data.createVariable('time', np.float32, 'time', fill_value=0)
        data.variables['time'][:] = np.array(oceanEnergy[i].timeIdx)
        # data.variables['time'].time = 'day'

        data.createVariable('MonMap', np.float32, ('mon', 'lat', 'lon'), fill_value=0)
        data.variables['MonMap'][:] = np.array(oceanEnergy[i].monPowerMap)
        # data.variable['MonMap'].MonMap = unit[i]

        data.createVariable('TimeSeries', np.float32, 'time', fill_value=0)
        data.variables['TimeSeries'][:] = np.array(oceanEnergy[i].timeSeries)
        # data.variables['TimeSeries'].TimeSeries = unit[i]

        data.site_lat = oceanEnergy[i].optSite[1][0]
        data.site_lon = oceanEnergy[i].optSite[1][1]
        data.avg = oceanEnergy[i].dailyAvg
        data.close()
