class SpotMarket(MiningSource):
  def __init__(self, zone='Tr.heim'):
    self.spot_prices = elspot.Prices()
    self.zone = zone

    self.sensor_name = 'spotmarket'

  def _initialize_data_structure(self):
    self.data = {
      'time': [],
      'prices': []
    }

  def _get_data(self):
    time_now = datetime.now(tz=LOCAL_TIMEZONE)
    time_noon = time_now.replace(second=0, microsecond=0, minute=0, hour=12)

    # Spot prices for next day are announces at noon every day
    if time_now > time_noon:
      day_list    = [0,1]
    else:
      day_list    = [0]

    for day in day_list:
      end_date = date.today() + timedelta(days=day)
      prices = self.spot_prices.hourly(areas=[self.zone], end_date=end_date)

      for i in range(24):
        timestamp = prices['areas'][self.zone]['values'][i]['start']  # UTC times
        timestamp = time.astimezone(LOCAL_TIMEZONE)                   # convert to local time
        price = prices['areas'][self.zone]['values'][i]['value']
        
        self.data['time'].append(time)
        self.data['prices'].append(price)