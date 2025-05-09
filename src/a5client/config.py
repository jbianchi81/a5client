import configparser
import os
from pathlib import Path
import platform

def get_windows_log_path() -> Path:
    base_dir = Path(os.getenv("LOCALAPPDATA")) # , Path.home() / "AppData" / "Local"
    log_dir = base_dir / "a5client" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "log.txt"

def get_log_path() -> Path:
    system = platform.system()

    if system == "Windows":
        base_dir = Path(os.getenv("LOCALAPPDATA"))
        log_dir = base_dir / "a5client" / "logs"
    elif system == "Darwin":  # macOS
        log_dir = Path.home() / "Library" / "Logs" / "a5client"
    else:  # Linux and others
        log_dir = Path.home() / ".local" / "share" / "a5client" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir / "a5client.log")

defaults = {
    "log": {
        "filename": get_log_path()
    },
    "server": {
        "url": "https://alerta.ina.gob.ar/a5",
        "token": "my_token"
    }
}

config_path = os.path.join(Path.home(),".a5client.ini")

def write_config(file_path : str = config_path, overwrite : bool = False, raise_if_exists : bool = False):
    config = configparser.ConfigParser()
    config.add_section("log")
    config.set("log","filename",defaults["log"]["filename"])
    config.add_section("server")
    config.set("server","url", defaults["server"]["url"])
    config.set("server","token", defaults["server"]["token"])
    if os.path.exists(file_path) and overwrite is False:
        if raise_if_exists:
            raise ValueError("Config file already exists")
    else:
        config.write(open(file_path,"w"))
        print("Default config file created: %s" % file_path)

def read_config(file_path : str = config_path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if not os.path.exists(file_path):
        try:
            write_config(file_path)
        except FileNotFoundError as e:
            print(str(e))
            raise FileNotFoundError("File not found and can't be created: %s" % file_path)
    config.read(file_path)
    return config


config = read_config()
