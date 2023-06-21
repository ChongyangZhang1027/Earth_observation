import numpy as np
import xarray as xr


class DataStruct:
    monEnergyMap = []  # monthly distribution map for three kinds of energy
    totalEnergyMap = []
    timeSeries = []  # daily time series for three kinds of energy
    timeIdx = []
    optSite = []
    dailyAvg = 0

    def _dataClear(self):
        self.distributionMap = []
        self.timeSeries = []


def readData(filePath, param):
    data_set = xr.open_dataset(filePath)
    data = data_set[param]
    return data


def saveDate(path, data):
    a = 0
