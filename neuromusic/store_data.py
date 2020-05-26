import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.abspath(''),".."))
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
import bci_workshop_tools as BCIw  # Our own functions for the workshop

################
#### Params ####
################
CHANNEL_NAMES = ['TP9','AF7','AF8','TP10']
file_name = input('What do you want to name your save file?')
FP_DATA_OUT = f'../data/{file_name}.csv'

# Search for active LSL stream
print('Looking for an EEG stream...')
streams = resolve_byprop('type', 'EEG', timeout=2)
if len(streams) == 0:
    raise RuntimeError('Can\'t find EEG stream.')

# Set active EEG stream to inlet and apply time correction
print("Start acquiring data")
inlet = StreamInlet(streams[0], max_chunklen=12)
eeg_time_correction = inlet.time_correction()

# Get the stream info and description
info = inlet.info()
description = info.desc()

# Get the sampling frequency
# This is an important value that represents how many EEG data points are
# collected in a second. This influences our frequency band calculation.
fs = int(info.nominal_srate())

""" 2. SET EXPERIMENTAL PARAMETERS """

# Length of the EEG data buffer (in seconds)
# This buffer will hold last n seconds of data and be used for calculations
buffer_length = 15

# Length of the epochs used to compute the FFT (in seconds)
epoch_length = 2

# Amount of overlap between two consecutive epochs (in seconds)
overlap_length = 1

# Amount to 'shift' the start of each next consecutive epoch
shift_length = epoch_length - overlap_length

# Index of the channel (electrode) to be used
# 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
index_channel = [1,2,3,4]
ch_names = ['AF7']  # Name of our channel for plotting purposes

# Get names of features
# ex. ['delta - CH1', 'pwr-theta - CH1', 'pwr-alpha - CH1',...]
feature_names = BCIw.get_feature_names(ch_names)

""" 3. INITIALIZE BUFFERS """

# Initialize raw EEG data buffer (for plotting)
eeg_buffer = np.zeros((int(fs * buffer_length), 1))
filter_state = None  # for use with the notch filter

# Compute the number of epochs in "buffer_length" (used for plotting)
n_win_test = int(np.floor((buffer_length - epoch_length) /
                            shift_length + 1))

# Initialize the feature data buffer (for plotting)
feat_buffer = np.zeros((n_win_test, len(index_channel)))


try:
    data_out = pd.DataFrame(columns=index_channel)
    while True:
        """ 3.1 ACQUIRE DATA """
        # Obtain EEG data from the LSL stream
        eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(shift_length * fs))
        epoch_dict={}
        for idx in index_channel:
            # Only keep the channel we're interested in
            ch_data = np.array(eeg_data)[:, idx]
            # Update EEG buffer
            eeg_buffer, filter_state = BCIw.update_buffer(
                    eeg_buffer, ch_data, notch=True,
                    filter_state=filter_state)

            """ 3.2 COMPUTE FEATURES """
            # Get newest samples from the buffer
            data_epoch = BCIw.get_last_data(eeg_buffer,
                                            epoch_length * fs)
            epoch_dict[idx]=np.array(data_epoch).reshape([-1,])
        data_out = data_out.append(pd.DataFrame(epoch_dict),ignore_index=True)
except KeyboardInterrupt:
    print(f'\nsaving {data_out.shape[0]} samples')
    data_out['time'] = np.arange(len(data_out))/fs
    data_out.to_csv(FP_DATA_OUT,index=False,header=CHANNEL_NAMES.append('time'))