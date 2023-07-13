import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

ssh_files = ['./workspace/data/MetO-NWS-PHY-hi-SSH-2022-01.nc']
wav_files = ['./workspace/data/MetO-NWS-WAV-2022-01.nc']
dataset = xr.open_dataset(ssh_files[0])

data = dataset['zos']
plt.plot(data[:, 1, 1])

dataset = xr.open_dataset(wav_files[0])
data = dataset['VHM0']
plt.plot(data[:, 1, 1])
plt.show()
# lat = dataset['lat']
# lon = dataset['lon']

