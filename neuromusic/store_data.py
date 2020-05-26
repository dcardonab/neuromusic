import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# sys.path.append(os.path.join(os.path.abspath(''),".."))
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
import bci_workshop_tools as BCIw  # Our own functions for the workshop

################
#### Params ####
################
FP_RAW_OUT = '../data/trial_raw.feather'
FP_FEATS_OUT = '../data/trial_features.feather'

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
fs = int(info.nominal_srate())
n_channels = info.channel_count()


# Get names of all channels
ch = description.child('channels').first_child()
ch_names = [ch.child_value('label')]
for i in range(1, n_channels):
    ch = ch.next_sibling()
    ch_names.append(ch.child_value('label'))

""" 2. SET EXPERIMENTAL PARAMETERS """

# Length of the EEG data buffer (in seconds)
# This buffer will hold last n seconds of data and be used for calculations
buffer_length = 15

# Length of the epochs used to compute the FFT (in seconds)
epoch_length = 2

# Amount of overlap between two consecutive epochs (in seconds)
overlap_length = 0.8

# Amount to 'shift' the start of each next consecutive epoch
shift_length = epoch_length - overlap_length

# Amount to 'shift' the start of each next consecutive epoch
shift_length = epoch_length - overlap_length

# Index of the channel (electrode) to be used
# 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
index_channel = [0, 1, 2, 3]
# Name of our channel for plotting purposes
ch_names = [ch_names[i] for i in index_channel]
n_channels = len(index_channel)

# Get names of features
# ex. ['delta - CH1', 'pwr-theta - CH1', 'pwr-alpha - CH1',...]
feature_names = BCIw.get_feature_names(ch_names)

""" 3. INITIALIZE BUFFERS """
# Initialize raw EEG data buffer (for plotting)
eeg_buffer = np.zeros((int(fs * buffer_length), n_channels))
filter_state = None  # for use with the notch filter

# Compute the number of epochs in "buffer_length" (used for plotting)
n_win_test = int(np.floor((buffer_length - epoch_length) /
                            shift_length + 1))

# Initialize the feature data buffer (for plotting)
feat_buffer = np.zeros((1,5)) #TODO This is TERRIBLE param handling

# Initialize the plots
plotter_eeg = BCIw.DataPlotter(fs * buffer_length, ch_names, fs)
plotter_feat = BCIw.DataPlotter(1, ['delta','theta','alpha','beta','gamma'],
                                1 / shift_length)
try:
    print('Press Ctrl-C in the console to break and save collected data.')
    raw_data_out = []
    feats_out = []
    while True:
        """ 3.1 ACQUIRE DATA """
        # Obtain EEG data from the LSL stream
        eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(shift_length * fs))
        epoch_dict={}

        # Only keep the channel we're interested in
        ch_data = np.array(eeg_data)[:, index_channel]
        
        # Update EEG buffer
        eeg_buffer, filter_state = BCIw.update_buffer(
                eeg_buffer, ch_data, notch=True,
                filter_state=filter_state)

        """ 3.2 COMPUTE FEATURES """
        # Get newest samples from the buffer
        data_epoch = BCIw.get_last_data(eeg_buffer,
                                        epoch_length * fs)


        # Compute features
        feat_vector = BCIw.compute_feature_vector(data_epoch,fs)
        feat_buffer, _ = BCIw.update_buffer(feat_buffer,feat_vector.values)
        

        """ 3.3 VISUALIZE THE RAW EEG AND THE FEATURES """
        plotter_eeg.update_plot(eeg_buffer)
        plotter_feat.update_plot(feat_buffer)
        plt.pause(0.00001)

        """ 3.4 STORE DATA FOR SAVING"""
        raw_data_out.append(pd.DataFrame(data_epoch,columns=ch_names))
        
        #add time to feat vector TODO This may not be ideal
        feat_vector['time'] = datetime.now()
        feats_out.append(feat_vector)
except KeyboardInterrupt:
    raw_data_out = pd.concat(raw_data_out,ignore_index=True)
    print(f'\nsaving {raw_data_out.shape[0]} samples from channels {raw_data_out.columns}')
    raw_data_out['time'] = np.arange(len(raw_data_out))/fs
    raw_data_out.to_feather(FP_RAW_OUT)

    feats_out = pd.concat(feats_out,ignore_index=True)
    feats_out.to_feather(FP_FEATS_OUT)
