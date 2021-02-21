from   nordpool import elspot, elbas
import requests
import json
import tibber
import numpy as np
import pickle
import sys
import sensibo_client as SC
import asyncio
from   datetime import date, datetime, timedelta, timezone
import pytz
import sched, time
import asyncio
from pathlib import Path
import os

LOCAL_TIMEZONE = pytz.timezone('Europe/Oslo')
# When you add the __init__() function to a child class, the child class will no longer inherit the parent's __init__() function.

class MiningSource():
  
  async def start_mining(self, measurement_sampling_time=60, time_ending=None):
    scheduled_time = self.get_first_scheduled_time(measurement_sampling_time)
    self.time_started = scheduled_time
    self.time_ending = time_ending
    
    while scheduled_time < self.time_ending or self.time_ending is None:
      time_now = datetime.now(tz=LOCAL_TIMEZONE)
      time_until_measurement = (scheduled_time - time_now).total_seconds()
      if time_until_measurement > 0:
          await asyncio.sleep(time_until_measurement)

      self.get_latest_measurement() # await?
      self.save_data_to_file()

      # set the time for next measurement
      scheduled_time += timedelta(minutes=measurement_sampling_time)

  def get_latest_measurement(self):
    # ha den spesiell for vær sensor?
    pass

  def save_data_to_file(self):
    # TODO: Store data after every update (overwriting current session file)
    # TODO: Store:
    # * daily
    # * weekly
    # * monthly
    # * yearly


    ## Maybe each have their own save_data_to_file function?
    # 1) initialize dirs
    # 2) prepare data for each directory
    # 3) store it in pickle format in each directory
    #     * overwrite if in current session
    #     * or start a new file if new day
    # See notion for file names and folder structure

    
    time_start = self.time_started_mining
    #time_end = str(datetime.now(tz=LOCAL_TIMEZONE))
    folder = self.sensor_name + '/'
    filename = self.sensor_name + "_" + time_start + '.pkl'
    # file = Path(filename)
    # if file.is_file() and :
    #   # Maybe do something different?
    #   with open(filename, "wb") as f:
    #     pickle.dump(self.data, f)
    # else:
    with open(folder+filename, "wb") as f:
      pickle.dump(self.data, f)
    return

  
  def get_first_scheduled_time(measurement_sampling_time):
    time_now = datetime.now(tz=LOCAL_TIMEZONE)
    dt = measurement_sampling_time
    if int(dt*np.ceil(time_now.minute/dt)) < 60:
        scheduled_time = time_now.replace(second=0,microsecond=0,minute=int(dt*np.ceil(time_now.minute/dt)))
    else:
        scheduled_time = time_now.replace(second=0,microsecond=0,minute=0,hour=time_now.hour+1)
    return scheduled_time