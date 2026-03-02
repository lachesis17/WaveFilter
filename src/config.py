import os
from configparser import ConfigParser

CONFIG_FILE = 'settings.ini'
CONFIG_DIR = 'settings'
CONFIG_FILE_FULL = os.path.join(CONFIG_DIR, CONFIG_FILE)

config = ConfigParser()


class ConfigManager():
    def __init__(self, config: ConfigParser = None):
        self.set_config(config)

    def set_config(self, config: ConfigParser):
        self.config = config if config is not None else self.get_config()

    def get_config(self):
        def set_default_config():
            config['last_accessed_folder'] = {
                'folder': ''
            }

        def write_file():
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
            with open(CONFIG_FILE_FULL, 'w') as file_handle:
                config.write(file_handle)

        if not os.path.exists(CONFIG_FILE_FULL):
            set_default_config()
            write_file()
        else:
            config.read(CONFIG_FILE_FULL)

        return config

    def get_last_directory(self):
        if 'folder' in self.config['last_accessed_folder']:
            folder_path = os.path.abspath(self.config['last_accessed_folder']['folder'])
        else:
            folder_path = os.getcwd()

        return folder_path

    def update_last_directory(self, fname: str):
        folder_path = os.path.dirname(os.path.abspath(fname))
        self.config['last_accessed_folder']['folder'] = folder_path
        with open(CONFIG_FILE_FULL, 'w') as configfile:
            self.config.write(configfile)
