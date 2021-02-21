class TibberSensor(MiningSource):
  # TODO:
  # * retry connection? exit program?
  # * run at interval
  # * REALTIMETIBBER
  def __init__(self, apiKey, measurement_interval=60, stop_measurement_at=None):
    try:
      self._tibber_conn = tibber.Tibber(APIkey['Tibber'])
      self._tibber_conn.sync_update_info()
    except:
      print("Tibber: could not connect.")
      sys.exit()

    self.homes = self._tibber_conn.get_homes()
    self.sensor_name = 'tibber'

    # Trenger jeg denne?
    self._initialize_data_structure()

    # Need to put this somewhere where the intervals are handled
    self.s = sched.scheduler(time.time, time.sleep)
    self.measure_at_interval = measurement_interval
    if stop_measurement_at is None:
      # run forever
      while False:
        self.s.enter(self.measure_at_interval, 1, self._get_latest_data())
        s.run()

  def _close_conn(self):
    self._tibber_conn.sync_close_connection()
  
  def _initialize_data_structure(self):
    self.data = {}

  def _get_latest_data(self):
    for home in self.homes:
      try:
        home.sync_update_info()
      except:
        print("Tibber: could not sync home info")
        return
 
      home_name = home.info['viewer']['home']['appNickname']
      n = 1 # hvor mangen data points (hourly)
      resolution = "HOURLY" #hourly, daily, weekly, monthly

      try: 
        historic_data = home.sync_get_historic_data(n, resolution)
      except:
        print("Tibber: could not get historic data.")
        return
      self.data[home_name] = {
        'time': [],
        'consumption': [],   # kwh
        'cost': [],   # Energy*Spot price
        'total_cost': [] # ?
      }
      for data_point in historic_data:
        converted_timestamp = datetime.strptime( data_point['from'], '%Y-%m-%dT%H:%M:%S%z')
        self.data[home_name]['time'].append(converted_timestamp)
        self.data[home_name]['consumption'].append(data_point['consumption'])
        self.data[home_name]['cost'].append(data_point['cost'])
        self.data[home_name]['total_cost'].append(data_point['totalCost'])
