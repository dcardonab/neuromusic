# neuromusic
Auralization of brain waves

## Getting started
I recomned using conda to create an environment specific to this project. To build a new conda env, replace `<ENV_NAME>` in the collowing command: `$ conda create --name <ENV_NAME> --file requirements.txt`

## Connecting the Muse EEG headset
In order to connect the headset, first turn it on and then from `$ neuromusic` run `$ make` to start streaming EEG data

## Data Collection
Once Muse is streaming run `python neuromusic/collect_data.py` to collect and save data to `data/`

## Visualize recordings
To see what was recorded and some basic features go to `data/initial_exploration.ipynb`. There's already some data saved so go ahead and check that out now! 