import configparser
import os
from pathlib import Path
import platform
from typing import TypedDict, Optional, Dict, cast
import json

class ServerConfigDict(TypedDict):
    url: str
    token: str
    proxy_dict: Optional[Dict[str, str]]
    timeout_connect: Optional[int]
    timeout_response: Optional[int]

class LogConfigDict(TypedDict):
    filename : str

class ConfigDict(TypedDict):
    server : ServerConfigDict
    log : LogConfigDict

def get_windows_log_path() -> Path:
    localappdata = os.getenv("LOCALAPPDATA")
    if localappdata is None:
        raise ValueError("environment variable LOCALAPPDATA not found")
    base_dir = Path(localappdata) # , Path.home() / "AppData" / "Local"
    log_dir = base_dir / "a5client" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "log.txt"

def get_log_path() -> Path:
    system = platform.system()

    if system == "Windows":
        localappdata = os.getenv("LOCALAPPDATA")
        if localappdata is None:
            raise ValueError("environment variable LOCALAPPDATA not found")
        base_dir = Path(localappdata)
        log_dir = base_dir / "a5client" / "logs"
    elif system == "Darwin":  # macOS
        log_dir = Path.home() / "Library" / "Logs" / "a5client"
    else:  # Linux and others
        log_dir = Path.home() / ".local" / "share" / "a5client" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return Path(str(log_dir / "a5client.log"))

defaults = {
    "log": {
        "filename": str(get_log_path())
    },
    "server": {
        "url": "https://alerta.ina.gob.ar/a5",
        "token": "my_token"
    }
}

config_path = os.path.join(Path.home(),".a5client.ini")

def parse_optional_int(value: str | None) -> Optional[int]:
    if value is None or value.strip() == "":
        return None
    return int(value)


def parse_proxy_dict(value: str | None) -> Optional[Dict[str, str]]:
    if value is None or value.strip() == "":
        return None
    # assume JSON in config
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("proxy_dict must be a dict")
    # enforce Dict[str, str]
    return {str(k): str(v) for k, v in data.items()}

def parse_config(cfg : configparser.ConfigParser) -> ConfigDict:
    if not cfg.has_section("log"):
        raise ValueError("Missing section: log")
    log_filename = cast(str, cfg["log"].get("filename", defaults["log"]["filename"]))
    return {
        "server": parse_server_config(cfg, "server"),
        "log": {
            "filename": log_filename
        }
    }

def parse_server_config(cfg : configparser.ConfigParser, section : str = "server") -> ServerConfigDict:
    if not cfg.has_section(section):
        raise ValueError(f"Missing section: {section}")

    s = cfg[section]

    try:
        result: ServerConfigDict = {
            "url": s["url"],
            "token": s["token"],
            "proxy_dict": parse_proxy_dict(s.get("proxy_dict")),
            "timeout_connect": parse_optional_int(s.get("timeout_connect")),
            "timeout_response": parse_optional_int(s.get("timeout_response")),
        }
    except KeyError as e:
        raise ValueError(f"Missing required key: {e}")

    return result


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

def read_config(file_path : str = config_path) -> ConfigDict:
    config = configparser.ConfigParser()
    if not os.path.exists(file_path):
        try:
            write_config(file_path)
        except FileNotFoundError as e:
            print(str(e))
            raise FileNotFoundError("File not found and can't be created: %s" % file_path)
    config.read(file_path)
    return parse_config(config)

config : ConfigDict = read_config()
