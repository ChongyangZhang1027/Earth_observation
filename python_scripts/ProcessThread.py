from PyQt5.QtCore import QThread, pyqtSignal
from os import popen

from algorithm import TidalEnergy, WaveEnergy, CurrEnergy
from DataModule import strAddZero


class processThread(QThread):
    signal = pyqtSignal(list)

    def __init__(self):
        super(processThread, self).__init__()
        self.filenames = None
        self.const = None
        print("Process thread created")

    def run(self):
        print("Enter process thread")
        currentEnergy = CurrEnergy(self.filenames[0], self.const)
        waveEnergy = WaveEnergy(self.filenames[0], self.const)
        tidalEnergy = TidalEnergy(self.filenames[1], self.const)
        self.signal.emit([tidalEnergy, waveEnergy, currentEnergy])


class downloadThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(downloadThread, self).__init__()
        print("Download thread created")
        self.workspacePath = ""
        self.monthCnt = 0
        self.timeRange = None
        self.boundary = None
        self.userName = ""
        self.passwd = ""

    def run(self):
        dataPath = "\"" + self.workspacePath + "/data/"
        for monIdx in range(self.monthCnt):
            year = self.timeRange[0][0] + int(monIdx / 12)
            nextYear = self.timeRange[0][0] + int((monIdx + 1) / 12)
            currMon = (self.timeRange[0][1] + monIdx) % 12
            nextMon = (currMon + 1) % 12
            if currMon == 0:
                currMon = 12
            currMon = strAddZero(str(currMon))
            if nextMon == 0:
                nextMon = 12
            nextMon = strAddZero(str(nextMon))
            cmdLine = "python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu --service-id " \
                      "NORTHWESTSHELF_ANALYSIS_FORECAST_WAV_004_014-TDS --product-id MetO-NWS-WAV-hi" \
                      + " --longitude-min " + str(self.boundary[0][1]) + " --longitude-max " + str(self.boundary[1][1])\
                      + " --latitude-min " + str(self.boundary[2][0]) + " --latitude-max " + str(self.boundary[0][0]) \
                      + " --date-min \"" + str(year) + "-" + currMon + "-01 00:00:00\"" \
                        " --date-max \"" + str(nextYear) + "-" + str(nextMon) + "-01 00:00:00\"" \
                        " --variable VHM0 --variable VSDX --variable VSDY --variable VTM02" \
                        " --out-dir " + dataPath + "\" --out-name MetO-NWS-WAV-" + str(year) + "-" + str(currMon) + \
                        ".nc --user " + self.userName + " --pwd " + self.passwd
            downMsg = popen(cmdLine).read()
            self.signal.emit("Downloading " + str(year) + "-" + currMon + "\n" + downMsg)
            cmdLine = "python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu --service-id " \
                      "NORTHWESTSHELF_ANALYSIS_FORECAST_PHY_004_013-TDS --product-id MetO-NWS-PHY-hi-SSH" \
                      + " --longitude-min " + str(self.boundary[0][1]) + " --longitude-max " + str(self.boundary[1][1])\
                      + " --latitude-min " + str(self.boundary[2][0]) + " --latitude-max " + str(self.boundary[0][0]) \
                      + " --date-min \"" + str(year) + "-" + currMon + "-01 00:00:00\"" \
                        " --date-max \"" + str(nextYear) + "-" + str(nextMon) + "-01 00:00:00\"" \
                        " --variable zos --out-dir " + dataPath + "\" --out-name MetO-NWS-PHY-hi-SSH-" + str(year) + \
                        "-" + str(currMon) + ".nc --user " + self.userName + " --pwd " + self.passwd
            downMsg = popen(cmdLine).read()
            self.signal.emit("Downloading " + str(year) + "-" + currMon + downMsg +
                             str(year) + "-" + currMon + " download finished\n")
