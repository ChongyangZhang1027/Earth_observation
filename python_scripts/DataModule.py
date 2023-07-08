from xarray import open_dataset
from netCDF4 import Dataset
from numpy import array, meshgrid, float32
import matplotlib.pyplot as plt


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
    data_set = open_dataset(filePath)
    data = data_set[param]
    return data


def strAddZero(timeStr):
    if len(timeStr) < 2:
        timeStr = '0' + timeStr
    return timeStr


def saveData(path, oceanEnergy):
    text = ["tidal", "wave", "current"]
    # unit = ["W/m^2", "kW/m", "W/m^2"]
    title0 = ['Tidal energy distribution ', 'Wave energy distribution ', 'Current energy distribution ']
    title = ['Tidal energy time series', 'Wave energy time series', 'Current energy time series']
    title2 = [' [W/m^2]', ' [kW/m]', ' [W/m^2]']
    yLabel = ['power [W/m^2]', 'power [kW/m]', 'power [W/m^2]']
    for i in range(3):
        data = Dataset(path + text[i] + '.nc', 'w', format='NETCDF4')

        data.createDimension('lat', len(oceanEnergy[i].lat))
        data.createDimension('lon', len(oceanEnergy[i].lon))
        data.createDimension('mon', len(oceanEnergy[i].monPowerMap))
        data.createDimension('time', len(oceanEnergy[i].timeSeries))

        data.createVariable('lat', float32, 'lat', fill_value=0)
        data.variables['lat'][:] = array(oceanEnergy[i].lat)
        # data.variables['lat'].lat = 'deg'

        data.createVariable('lon', float32, 'lon', fill_value=0)
        data.variables['lon'][:] = array(oceanEnergy[i].lon)
        # data.variables['lon'].lon = 'deg'

        data.createVariable('time', float32, 'time', fill_value=0)
        data.variables['time'][:] = array(oceanEnergy[i].timeIdx)
        # data.variables['time'].time = 'day'

        data.createVariable('MonMap', float32, ('mon', 'lat', 'lon'), fill_value=0)
        data.variables['MonMap'][:] = array(oceanEnergy[i].monPowerMap)
        # data.variable['MonMap'].MonMap = unit[i]

        data.createVariable('TimeSeries', float32, 'time', fill_value=0)
        data.variables['TimeSeries'][:] = array(oceanEnergy[i].timeSeries)
        # data.variables['TimeSeries'].TimeSeries = unit[i]

        data.site_lat = oceanEnergy[i].optSite[1][0]
        data.site_lon = oceanEnergy[i].optSite[1][1]
        data.avg = oceanEnergy[i].dailyAvg
        data.close()

        # save time series
        plt.figure()
        if i == 1:
            plt.plot(oceanEnergy[i].timeIdx, array(oceanEnergy[i].timeSeries) / 1000, marker='.')
        else:
            plt.plot(oceanEnergy[i].timeIdx, oceanEnergy[i].timeSeries, marker='.')
        plt.title(title[i])
        plt.xlabel('time [day]')
        plt.ylabel(yLabel[i])
        plt.grid()
        plt.savefig(path + title[i] + '.png')
        plt.show()
        plt.close()

        # save distribution map
        plt.figure()
        lon, lat = meshgrid(oceanEnergy[i].lon, oceanEnergy[i].lat)
        if i == 1:
            plt.pcolor(lon, lat, oceanEnergy[i].totalPowerMap / 1000)
        else:
            plt.pcolor(lon, lat, oceanEnergy[i].totalPowerMap)
        plt.title(title0[i] + "average" + title2[i])
        plt.xlabel('lon [deg]')
        plt.ylabel('lat [deg]')
        plt.colorbar()
        plt.scatter(oceanEnergy[i].optSite[1][1], oceanEnergy[i].optSite[1][0], marker='^')
        plt.savefig(path + title0[i] + 'average.png')
        plt.show()
        plt.close()
