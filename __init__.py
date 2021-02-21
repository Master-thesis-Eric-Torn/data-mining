from data_mining.data_sources import SensiboHome, TibberSensor, WeatherAPI, SpotMarket

# TODO:
# * import classes
# * start running and storing data

# Get arguments
# Initialize stuff
# Start mining at interval

# Config
config = {
  "store_together": True,
  "measurement_interval": 60,
  "store_data_at_interval": 60
}

class DataMiner():
  def __init__(self, tibber_api_key=None, sensibo_api_key=None, weather_api_key=None):
    self.sensiboHome = SensiboHome(sensibo_api_key)
    self.tibberSensor = TibberSensor(tibber_api_key)
    self.weatherAPI = WeatherAPI(weather_api_key)
    self.spotMarket = SpotMarket()

    self.measurement_interval = config["measurement_interval"]
    self.store_data_at_interval = config["store_data_at_interval"]
    self.store_together = config["store_together"]

    self.settings = {

    }
    self.sensiboHome.measurement_interval = 60

  def settings(self, measurement_interval=None):
    if measurement_interval and type(measurement_interval) == int:
      self.measurement_interval = measurement_interval
    return

  def start(self):
    asyncio.run(_async_start())

    while True:
      # backup_data() at interval
      pass
    return

  async def _async_start_mining(self):
    await asyncio.gather(
      self.sensiboHome.start_mining(
        # measurement_interval = self.measurement_interval,
        # end_time = None
        ),
      self.tibberSensor.start_mining(self.measurement_interval),
      self.weatherAPI.start_mining(self.measurement_interval),
      self.spotMarket.start_mining(self.measurement_interval),
      
      self._async_backup_data()
    )

    print("Mining stopped.")
    return

  async def _async_backup_data(self):
    # TODO: BACKUP DATA AT INTERVAL OR REQUEST
    # TODO: Put together into a collective file
    # TODO: Store as: daily, weekly, monthly

    data_output = {}
    data_output["sensibo"] = self.sensiboHome.data
    data_output["tibber"] = self.tibberSensor.data
    data_output["weather"] = self.weatherAPI.data
    data_output["spot_market"] = self.spotMarket.data
    
    filename = "together_" + str(datetime.now()) + ".pkl"
    with open(filename, "wb") as f:
      pickle.dump(data_output)
    return True
