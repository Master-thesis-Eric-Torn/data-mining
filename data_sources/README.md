# Data Mining
=============

Gets data from:
- TibberAPI
- Sensibo Home sensors
- Open Weather Map API

## Usage
1. Import the package
2. Set parameters
   - All sensors are optional, and the data_miner will only run the ones you provide in the parameter dictionary. For example, removing the 'tibber' key and its data from params will make the dataMiner only collect data for sensibo and weather.
3. Initialize a dataMining object
4. dataMining.start()

```python
import data_mining

params = {
    'tibber': { # (optional)
        'api_key': 'some-key', # REQUIRED
        'sampling_time': 60*60,   # [seconds] (optional)
        'end_mining_at': None  # [datetime] (optional)
    },
    'sensibo': { # (optional)
        'api_key': 'some-key', # REQUIRED
        'sampling_time': 5*60,   # [seconds] (optional)
        'end_mining_at': None  # [datetime] (optional)
    },
    'weather': { # (optional)
        'api_key': 'some-key', # REQUIRED
        'lat': "63.4",         # REQUIRED
        'lon': "10.335",       # REQUIRED
        'sampling_time': 60*60,   # [seconds] (optional)
        'end_mining_at': None  # [datetime] (optional)
    },
    'backup': { # (optional)
        'run_backups': True, # [bool] (optional)
        'end_backups_at': None # [datetime] (optional)
    }
}

dataMiner = data_mining.DataMiner(params)
dataMiner.start()
```

## Default parameter values
```python
DEFAULT = {
    "sampling_time": 60*60, # [seconds]
    "end_mining_at": None,
    "run_backups": True,
    "end_backup_at": None,
}
```
