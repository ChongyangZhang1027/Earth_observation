import xarray as xr
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


def saveData(path, data):
    a = 0
