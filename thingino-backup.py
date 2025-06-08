import logging
import os
import schedule
import subprocess
import sys
import time
import yaml

config_file = '/thingino/config.yaml'
backup_root = '/thingino/backups/'
backup_suffix = '/x/tool-upgrade.cgi?action=generate_backup'

config_file_exists = os.path.exists(config_file)
backup_root_exists = os.path.exists(backup_root)

if config_file_exists:
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    log_level = config['log_level'].upper() if 'log_level' in config else 'INFO'
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s: %(message)s')
else:
    logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s: %(message)s')
    logging.error('No configuration file found.')
    sys.exit(1)

if not backup_root_exists:
    os.mkdir(backup_root)
    logging.info(f'Creating backup directory at {backup_root}')

auto_backup_enabled = 'auto_backup' in config

if auto_backup_enabled:
    max_backups = int(config['auto_backup']['max_backups']) if 'max_backups' in config['auto_backup'] else 5
    logging.info(f'Max backup count set to {max_backups}.')
else:
    logging.warning('Auto-backup is not enabled. Backup will run once and then exit.')

class ThinginoDevice:
    def __init__(self):
        self.user = 'root'
        self.devices = {}
    
    def get_device_configs(self, dev_name):
        """Read config file and store device info"""
        devices = config['devices']
        self.devices[dev_name] = {}
        self.devices[dev_name]['hostname'] = devices[dev_name]['hostname']
        self.devices[dev_name]['user'] = self.user
        self.devices[dev_name]['password'] = devices[dev_name]['password']
        self.devices[dev_name]['backup_dir'] = f'{backup_root}{dev_name.lower().replace(" ","-")}'

    def create_dirs(self, dev_name):
        """Create backup directories if they don't already exist"""
        dir = self.devices[dev_name]['backup_dir']
        if not os.path.exists(dir):
            logging.debug(f'Creating backup directory for {device}.')
            os.mkdir(dir)

    def initial_backup(self, dev_name):
        backup_dir = self.devices[dev_name]['backup_dir']
        backup_list = os.listdir(backup_dir)
        backup_count = len(backup_list)
        if backup_count < 1:
            d.get_backup(dev_name)

    def get_backup(self, dev_name):
        """Connect to Thingino device and fetch backup file"""
        hostname = self.devices[dev_name]['hostname']
        user = self.devices[dev_name]['user']
        passwd = self.devices[dev_name]['password']
        backup_dir = self.devices[dev_name]['backup_dir']
        try:
            logging.debug(f'Fetching backup for {dev_name}.')
            # please don't judge me for this
            subprocess.check_output(f'wget -q -N -T 5 -t 2 --user {user} --password {passwd} \
                                    --content-disposition http://{hostname}{backup_suffix} \
                                    -P {backup_dir}', shell=True)
        except Exception as e:
            logging.error(f'Unable to fetch backup file for {dev_name}: {e}')

    def delete_old_backups(self, dev_name):
        """Delete oldest backup file in each device's backup directory"""
        backup_dir = self.devices[dev_name]['backup_dir']
        backup_list = os.listdir(backup_dir)
        backup_count = len(backup_list)
        backup_path = [f'{backup_dir}/{x}' for x in backup_list]
        logging.debug(f'Deleting oldest backup file(s) for {device}.')
        while backup_count > max_backups:
            backup_list = os.listdir(backup_dir)
            backup_count = len(backup_list)
            if backup_count > max_backups:
                backup_path = [f'{backup_dir}/{x}' for x in backup_list]
                oldest_backup = min(backup_path, key=os.path.getctime)
                os.remove(oldest_backup)

    def auto_backup(self):
        """Used to retrieve backups if auto-backup is enabled"""
        for device in self.devices.keys():
            d.get_backup(device)

    def auto_delete(self):
        """Used to delete old backups if auto-backup is enabled"""
        for device in self.devices.keys():
            d.delete_old_backups(device)

d = ThinginoDevice()

if __name__ == '__main__':
    for device in config['devices'].keys():
        d.get_device_configs(device)
        d.create_dirs(device)
        d.initial_backup(device)
    
    if auto_backup_enabled:
        schedule.every().day.at("03:00").do(d.auto_backup)
        schedule.every().day.at("03:30").do(d.auto_delete)
        while True:
            schedule.run_pending()
            time.sleep(10)
    else:
        for device in config['devices'].keys():
            d.get_backup(device)
            sys.exit(0)