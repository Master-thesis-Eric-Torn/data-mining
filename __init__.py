# Flake8: noqa
from   nordpool import elspot, elbas
import requests
import json
import tibber
import numpy as np
import pickle
import sys
import sensibo_client as SC
import asyncio
from   datetime import date, datetime, timedelta
import pytz
import sched, time

# TODO:
# Er på GetPumps function i House.....py
# measurement interval in seconds?
# rydde

# Hva slags data trenger jeg?
## Tibber
## Sensibo

# Properties/Arguments
## Sampling time (hva er default oppdatering for sensibo/tibber? per time?)
### temperature
### pumps
### power
## API key
### Sensibo
### tibber
### weather
#### Position lat lng zone

# Modules
## Scheduler
## Heat pumps (sensibo?)
## Tibber

# Sensibo
## measurement
# {'time': {'secondsAgo': 50, 'time': '2021-02-15T12:09:36.571151Z'},
#  'temperature': 19.5,
#  'humidity': 45.6}
## state
# {'on': True,
#  'fanLevel': 'medium_high',
#  'timestamp': {'secondsAgo': 0, 'time': '2021-02-15T12:11:07.722080Z'},
#  'temperatureUnit': 'C',
#  'horizontalSwing': 'fixedCenter',
#  'targetTemperature': 20,
#  'mode': 'heat',
#  'swing': 'fixedMiddleTop'}

class SensiboHome():
  def __init__(self, apiKey, measurement_interval=60, stop_measurement_at=None):
    try:
      SensiboHome = SC.SensiboClientAPI(apiKey)
    except:
      print('Home Sensibo could not be accessed. Code terminated.')
      sys.exit()
    
    # Initialize connection to sensibo account/home
    self.home = SensiboHome
    self.devices = self.home.devices()

    # Configuration    
    self.what_to_measure = ['temperature', 'humidity']
    self.states_to_record = ['on','targetTemperature','fanLevel','mode']
    self.measure_at_interval = measurement_interval # seconds
    self.localTimeZone = pytz.timezone('Europe/Oslo')

    # Measurement properties
    self.time_since_last_measurement = None

    # Call api for latest measurements and state
    self.pumpsData = {}
    self._get_latest_pump_data()
    self.s = sched.scheduler(time.time, time.sleep)
    
    # Need to put this somewhere where the intervals are handled
    if stop_measurement_at is None:
      # run forever
      while False:
        self.s.enter(self.measure_at_interval, 1, self._get_latest_pump_data())
        s.run()

  def initialize_data_structure(self):
    for pump in self.devices.keys():
      self.pumpsData[pump]  =  {'times': [],
                                'measurements': {},
                                'states': {}}

      for measurementType in self.what_to_measure:
        self.pumpsData[pump]['measurements'][measurementType] = []

      for state in self.states_to_record:
        self.pumpsData[pump]['states'][state] = []


  def _get_latest_pump_data(self):
    for pump in self.devices.keys():
      try:
        latestMeasurement = self.home.pod_measurement(self.devices[pump])[0]
        currentState = self.home.pod_ac_state(self.devices[pump])

        if self.time_since_last_measurement != None and latestMeasurement['time']['secondsAgo'] >= self.time_since_last_measurement:
          print("Sensibo data: Latest measurement was already recorded. Aborting until next interval to avoid duplicates.")
          return
        
        for measurementType in self.pumpsData[pump]['measurements'].keys():
            if measurementType in latestMeasurement:
              self.pumpsData[pump]['measurements'][measurementType].append(latestMeasurement[measurementType])
            else:
              self.pumpsData[pump]['measurements'][measurementType].append(np.NaN)
              print(latestMeasurement)
              print('Measurement '+str(measurementType)+' for '+str(pump)+' missing, put NaN ')
        
        for state in self.pumpsData[pump]['States']:
            if state in currentState:
              self.pumpsData[pump]['States'][state].append(currentState[state])
            else:
              self.pumpsData[pump]['States'][state].append(np.NaN)
              print(currentState)
              print('State '+str(state)+' for '+str(pump)+' missing, put NaN ')
                
        timestamp = datetime.strptime(latestMeasurement['time']['time'],'%Y-%m-%dT%H:%M:%S.%fZ')
        utcTimestamp = timestamp.replace(tzinfo=pytz.utc)
        pumpsData[pump]['times'].append(utcTimestamp.astimezone(tz=self.localTimeZone))
        self.time_since_last_measurement = latestMeasurement['time']['secondsAgo']
      except:
        print('Measurement or state for '+str(pump)+' not available ')        


class TibberSensor():
  def __init__(self, apiKey):
    pass


class WeatherAPI():
  def __init__(self, lat, lon, apiKey):
    self.lat = lat
    self.lon = lon
    self.apiKey = apiKey
    self.url  = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={apiKey}&units=metric"
    
    asyncio.run(self.request_data_from_api())

  async def request_data_from_api(self):
    try:
      response = await requests.get(self.url, timeout=30)
      if response.status_code == 200:
        data = json.loads(response.text)
        self.lastUpdated = response.headers["Date"]
        self.daily = data["daily"]
        self.hourly = data["hourly"]
        self.minutely = data["minutely"]
        self.current = data["current"]
    except:
      print("Could not get request from the URL. Check API key, lat, or lon.")


class SpotMarket():
  def __init__(self, zone, numDays):
    # Initialize Nordpool spot prices
    endDay = date.today() + timedelta(days=numDays)
    spotPrices = elspot.Prices()
    hourlySpotPrices = spotPrices.hourly(areas=zone, end_date=endDay)


# Text file with numpy?
x = np.linspace(0, 1, 201)
y = np.random.random(201)
data = np.column_stack((x, y))
header = "X-Column, Y-Column"
np.savetxt('AB_data.txt', data, header=header)

data = np.loadtxt('AB_data.txt')
x = data[:, 0]
y = data[:, 1]

print(x)
print(y)

# pickle
DataPickle = {'Energy': 'DataEnergy',
              'HP': 'DataHP',
              'Weather': 'WeatherLog'}

f = open('data.pkl', "wb")
pickle.dump(DataPickle, f)
f.close()


##############

