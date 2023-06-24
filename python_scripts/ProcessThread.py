from PyQt5.QtCore import QThread, pyqtSignal
from algorithm import TidalEnergy, WaveEnergy, CurrEnergy


class processThread(QThread):
    signal = pyqtSignal(list)

    def __init__(self):
        super(processThread, self).__init__()
        self.filenames = None
        print("Thread created")

    def run(self):
        print("enter thread")
        currentEnergy = CurrEnergy(self.filenames[0])
        waveEnergy = WaveEnergy(self.filenames[0])
        tidalEnergy = TidalEnergy(self.filenames[1])
        self.signal.emit([currentEnergy, waveEnergy, tidalEnergy])
