from data_mining.data_sources import TibberAPI, SensiboSensor, WeatherAPI
import zipfile
from datetime import datetime, timedelta
import pytz
from pathlib import Path
import logging
import atexit
import asyncio
import nest_asyncio
nest_asyncio.apply()

LOCAL_TIMEZONE = pytz.timezone('Europe/Oslo')
DEFAULT = {
    "sampling_time": 60*60,
    "end_mining_at": None,
    "end_backup_at": None,
    "max_backup_copies": 5
}


class DataMiner():
    '''
    Data Mining module
    ==================
    Saves data from:
    * TibberAPI
    * Sensibo
    * Open Weather Map API

    Stores in files as pickle format.

    Backups are by default ran once every day at midnight, as well as whenever the program exits.
    '''
    def __init__(self, params={}):
        logging.basicConfig(filename="datamining_errors.log",
                            format='%(asctime)s %(message)s', level=logging.DEBUG)
        atexit.register(self._backup, object_to_backup='data', backup_folder='backups')
        self._mining_coroutines = []
        # Initialize all sensors which has been provided an API key
        try:
            tibber = params['tibber']
            sampling_time = tibber.get('sampling_time', DEFAULT["sampling_time"])
            end_mining_at = tibber.get('end_mining_at', DEFAULT["end_mining_at"])
            self.tibberAPI = TibberAPI(
                    api_key = tibber['api_key'],
                    sampling_time = sampling_time,
                    end_mining_at = params['tibber']['end_mining_at']
                )
            self._mining_coroutines.append(self.tibberAPI.start_mining())
        except:
            print("Tibber api_key not found in parameters. Will not include tibber in data mining.")

        try:
            sensibo = params['sensibo']
            sampling_time = sensibo.get('sampling_time', DEFAULT["sampling_time"])
            end_mining_at = sensibo.get('end_mining_at', DEFAULT["end_mining_at"])
            self.sensiboSensor = SensiboSensor(
                    api_key = sensibo['api_key'],
                    sampling_time = sampling_time,
                    end_mining_at = end_mining_at
                )
            self._mining_coroutines.append(self.sensiboSensor.start_mining())
        except:
            print("Sensibo api_key not found in parameters. Will not include sensibo in data mining.")

        try:
            weather = params['weather']
            sampling_time = weather.get('sampling_time', DEFAULT["sampling_time"])
            end_mining_at = weather.get('end_mining_at', DEFAULT["end_mining_at"])
            self.weatherAPI = WeatherAPI(
                    api_key = params['weather']['api_key'], 
                    sampling_time = sampling_time,
                    end_mining_at = end_mining_at,
                    lat = params['weather']['lat'],
                    lon = params['weather']['lon']
                )
            self._mining_coroutines.append(self.weatherAPI.start_mining())
        except:
            print("Weather api_key, latiture or longitude not found in parameters. Will not include sensibo in data mining.")

        # Backups parameters
        self.end_backup_time = DEFAULT["end_backup_at"]
        try:
            backup_params = params['backup']
            self.run_backups = backup_params.get('run_backups', False)
            self.end_backup_time = backup_params.get('end_backups_at', DEFAULT["end_backup_at"])
        except:
            self.run_backups = True
            print("Backup parameters not found, running with default backup params: run_backups=True, end_backup_at=None")
        
        print("-----------------")


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
        end_backup_time = self.end_backup_time if self.end_backup_time else "Never"
        print(f"Backups started | next backup: {scheduled_time} | ending: {end_backup_time}")
        
        while self.end_backup_time is None or scheduled_time < self.end_backup_time:
            time_now = datetime.now(tz=LOCAL_TIMEZONE)
            time_until_backup = (scheduled_time - time_now).total_seconds()
            if time_until_backup > 0:
                await asyncio.sleep(time_until_backup)
            
            backup_success = self._backup('data', 'backups')
            success_message = ""
            if backup_success:
                success_message += f"BACKUP | {scheduled_time} | Success: backuped files in /backups/"
            
            scheduled_time += timedelta(hours=24)
            
            if success_message:
                message = f"{success_message} | Next backup at: {scheduled_time}"
                logging.info(message)
                print(message)
        return

    def _backup(self, object_to_backup, backup_folder):
        # settings
        max_backup_copies = DEFAULT["max_backup_copies"]

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
            if x.is_file() and x.suffix == '.zip' and x.name.startswith('data_backup')
        ]

        # Enforce max backups and delete oldest if there will be too many after the new backup
        oldest_to_newest_backup_by_name = list(sorted(existing_backups, key=lambda f: f.name))
        while len(oldest_to_newest_backup_by_name) >= max_backup_copies:  # >= because we will have another soon
            backup_to_delete = oldest_to_newest_backup_by_name.pop(0)
            backup_to_delete.unlink()

        # Create zip file (for both file and folder options)
        backup_file_name = f'{object_to_backup_path.name}_backup__{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.zip'
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
