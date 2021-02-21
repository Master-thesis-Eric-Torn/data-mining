class WeatherAPI(MiningSource):
  def __init__(self, lat, lon, apiKey):
    self.lat = lat
    self.lon = lon
    self.apiKey = apiKey
    self.url  = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely&exclude=daily&exclude=alerts&appid={apiKey}&units=metric"
    
    self.sensor_name = 'weather'

    asyncio.run(self.request_data_from_api())

  def _initialize_data_structure(self):
    self.historic_data = {
      'time': [],
      'temperature': []
    }
    self.current = {}

  async def request_data_from_api(self):
    try:
      response = await requests.get(self.url, timeout=30)
      if response.status_code == 200:
        data = json.loads(response.text)
        for item in data["hourly"]:
          timestamp = datetime.utcfromtimestamp(item['dt']).replace(tzinfo=timezone.utc)
          timestamp = timestamp.astimezone(LOCAL_TIMEZONE)
          self.historic_data["time"].append(timestamp)
          self.historic_data["time"].append(item["temp"])
        
        current_timestamp = datetime.utcfromtimestamp(data["current"]["dt"]).replace(tzinfo=timezone.utc)
        current_timestamp = timestamp.astimezone(LOCAL_TIMEZONE)
        self.current["time"] = current_timestamp
        self.current["temperature"] = data["current"]["temp"]
        self.last_updated = response.headers["Date"]
    except:
      print("Weather API: Could not get request from the URL. Check API key, lat, or lon.")