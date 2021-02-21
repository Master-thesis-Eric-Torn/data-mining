class SensiboHome(MiningSource):
  def __init__(self, apiKey):
    super().__init__()
    try:
      SensiboHome = SC.SensiboClientAPI(apiKey)
    except:
      print('Home Sensibo could not be accessed. Code terminated.')
      sys.exit()

    self.sensor_name = 'sensibo'
    
    # Initialize connection to sensibo account/home
    self.home = SensiboHome
    self.devices = self.home.devices()
    
    # Configuration    
    self.what_to_measure = ['temperature', 'humidity']
    self.states_to_record = ['on','targetTemperature','fanLevel','mode']
#   self.measure_at_interval = measurement_interval # seconds
    self.localTimeZone = pytz.timezone('Europe/Oslo')

    # Measurement properties
    self.time_since_last_measurement = None

    # Call api for latest measurements and state
    self.pumpsData = {}
    self._initialize_data_structure()
    self._get_latest_pump_data()


  def _initialize_data_structure(self):
    for pump in self.devices.keys():
      self.pumpsData[pump]  =  {'times': [],
                                'measurements': {},
                                'states': {}}

      for measurementType in self.what_to_measure:
        self.pumpsData[pump]['measurements'][measurementType] = []

      for state in self.states_to_record:
        self.pumpsData[pump]['states'][state] = []


  async def _async_get_latest_pump_data(self):
    for pump in self.devices.keys():
      try:
        latestMeasurement = await self.home.pod_measurement(self.devices[pump])[0]
        currentState = await self.home.pod_ac_state(self.devices[pump])

        if self.time_since_last_measurement != None and latestMeasurement['time']['secondsAgo'] >= self.time_since_last_measurement:
          print("Sensibo data: Latest measurement was already recorded. Aborting until next interval to avoid duplicates.")
          return False
        
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
    return True