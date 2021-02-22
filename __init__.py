from data_mining.data_sources import TibberAPI, SensiboSensor, WeatherAPI
import zipfile
from datetime import datetime
import pytz
from pathlib import Path
import asyncio

'''
Data Mining module
==================
'''
LOCAL_TIMEZONE = pytz.timezone('Europe/Oslo')
DEFAULT = {
    "sampling_time": 60*60,
}

# params = {
#     'tibber': {
#         'api_key': 'dx61b7ne2HzGbpt0gI0xrB1f0jxd0_heXs-dmoMcnuA',
#         'sampling_time': 60*60,
#         'end_mining_at': None
#     },
#     'sensibo': {
#         'api_key': 'tXZ5Ibk5s95UZgZgOU3wzJ4MOunl2f',
#         'sampling_time': 5*60,
#         'end_mining_at': None
#     },
#     'weather': {
#         'api_key': 'c512438f8c9099db879c8fec88b10111',
#         'lat': "63.4",
#         'lon': "10.335",
#         'sampling_time': 60*60,
#         'end_mining_at': None
#     },
#     'backup': {
#         'run_backups': True,
#         'end_backups_at': None
#     }
# }

# ########
# # USAGE
# dataMiner = DataMiner(params)
# dataMiner.start()
# toThread(dataMiner.start_backups())

# # For raspberry:
# dataMiner = DataMiner(params)
# toThread(dataMiner.start())
# toThread(dataMiner.start_backups())


# TODO:
# * Add he initial sensor parameters below to the __init__ in sensors


class DataMiner():
    def __init__(self, params):
        self._mining_coroutines = []
        # Initialize all sensors which has been provided an API key
        if params['tibber']['api_key']:
            sampling_time = params['tibber']['sampling_time']
            self.tibberAPI = TibberAPI(
                    api_key = params['tibber']['api_key'], 
                    sampling_time = sampling_time if sampling_time else DEFAULT["sampling_time"],
                    end_mining_at = params['tibber']['end_mining_at']
                )
            self._mining_coroutines.append(self.tibberAPI.start_mining())

        if params['sensibo']['api_key']:
            sampling_time = params['sensibo']['sampling_time']
            self.sensiboSensor = SensiboSensor(
                    api_key = params['sensibo']['api_key'],
                    sampling_time = sampling_time if sampling_time else DEFAULT["sampling_time"],
                    end_mining_at = params['sensibo']['end_mining_at']
                )
            self._mining_coroutines.append(self.sensiboSensor.start_mining())

        if params['weather']['api_key']:
            sampling_time = params['weather']['sampling_time']
            self.weatherAPI = WeatherAPI(
                    api_key = params['weather']['api_key'], 
                    sampling_time = sampling_time if sampling_time else DEFAULT["sampling_time"],
                    end_mining_at = params['weather']['end_mining_at'],
                    lat = params['weather']['lat'],
                    lon = params['weather']['lon']
                )
            self._mining_coroutines.append(self.weatherAPI.start_mining())

        # Backups parameters
        if params['backup']['run_backups'] == True:
            self.run_backups = True
            self.end_backup_time = params['backup']['end_backups_at']

    def start(self):
        asyncio.run(self._async_start())
        return

    async def _async_start(self):

        await asyncio.gather(
            *self._mining_coroutines,
            self._async_backup_data()
        )
        print("Mining stopped.")
        return

    async def _async_backup_data(self):
        if self.run_backups == False:
            return

        scheduled_time = self._get_midnight_time()
        while self.end_backup_time is None or scheduled_time < self.end_backup_time:
            time_now = datetime.now(tz=LOCAL_TIMEZONE)
            time_until_backup = (scheduled_time - time_now).total_seconds()
            if time_until_backup > 0:
                await asyncio.sleep(time_until_backup)
            self._backup('data', 'backups')
            scheduled_time += timedelta(seconds=self.sampling_time)
        return

    def _backup(self, object_to_backup, backup_folder):
        # settings
        max_backups_amount = 5

        # Setup paths and folder
        object_to_backup_path = Path(object_to_backup)
        backup_directory_path = Path(backup_folder)
        if not object_to_backup_path.exists():
            print("Backup: object does not exist")
            return False
        backup_directory_path.mkdir(parents=True, exist_ok=True)

        # check how many existing backups exist
        existing_backups = [
            x for x in backup_directory_path.iterdir()
            if x.is_file() and x.suffix == '.zip' and x.name.startswith('backup-')
        ]

        # Enforce max backups and delete oldest if there will be too many after the new backup
        oldest_to_newest_backup_by_name = list(sorted(existing_backups, key=lambda f: f.name))
        while len(oldest_to_newest_backup_by_name) >= max_backups_amount:  # >= because we will have another soon
            backup_to_delete = oldest_to_newest_backup_by_name.pop(0)
            backup_to_delete.unlink()

        # Create zip file (for both file and folder options)
        backup_file_name = f'backup-{datetime.now().strftime("%Y%m%d%H%M%S")}-{object_to_backup_path.name}.zip'
        zip_file = zipfile.ZipFile(str(backup_directory_path / backup_file_name), mode='w')
        if object_to_backup_path.is_file():
            # If the object to write is a file, write the file
            zip_file.write(
                object_to_backup_path.absolute(),
                arcname=object_to_backup_path.name,
                compress_type=zipfile.ZIP_DEFLATED
            )
        elif object_to_backup_path.is_dir():
            # If the object to write is a directory, write all the files
            for file in object_to_backup_path.glob('**/*'):
                if file.is_file():
                    zip_file.write(
                        file.absolute(),
                        arcname=str(file.relative_to(object_to_backup_path)),
                        compress_type=zipfile.ZIP_DEFLATED
                    )
        zip_file.close()
        return True
    
    def _get_midnight_time(self):
        time_now = datetime.now(tz=LOCAL_TIMEZONE)
        midnight = time_now.replace(microsecond=0, second=0, minute=0, hour=0, day=time_now.day+1)
        return midnight

    def set_settings(self):
        # TODO: return all settings/parameters
        # self.sensiboSensor.some_setting = something
        # self.sensiboSensor.some_other_setting = somethingElse
        return
    
    def get_settings(self):
        # TODO: not a priority
        settings = {}
        return settings

    async def _async_store_data_together(self):
        # TODO
        # put together at every hour?

        # Timeschedule
        # while
        #   backup
        #   timeschedule
        #   asyncio sleep
        pass