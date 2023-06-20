import numpy as np
import xarray as xr


class DataStruct:
    distributionMap = []  # monthly distribution map for three kinds of energy
    timeSeries = [[], [], []]  # daily time series for three kinds of energy


def readData(filePath, param):
    data_set = xr.open_dataset(filePath)
    data = data_set[param]
    return data


def saveDate(path, data):
    a = 0
