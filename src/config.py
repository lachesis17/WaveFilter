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

    def get_line_colors(self) -> dict:
        defaults = {'raw': '200,200,200', 'filtered': '150,0,255', 'fft': '0,200,0'}
        if 'line_colors' not in self.config:
            return {k: tuple(int(x) for x in v.split(',')) for k, v in defaults.items()}
        section = self.config['line_colors']
        result = {}
        for key, default in defaults.items():
            raw = section.get(key, default)
            try:
                result[key] = tuple(int(x) for x in raw.split(','))
            except ValueError:
                result[key] = tuple(int(x) for x in default.split(','))
        return result

    def set_line_colors(self, colors: dict):
        if 'line_colors' not in self.config:
            self.config['line_colors'] = {}
        for key, rgb in colors.items():
            self.config['line_colors'][key] = ','.join(str(c) for c in rgb)
        with open(CONFIG_FILE_FULL, 'w') as configfile:
            self.config.write(configfile)
