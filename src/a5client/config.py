import configparser
import os

defaults = {
    "log": {
        "filename": "/var/log/a5client.log"
    }
}

config_path = os.path.join(os.environ["HOME"],".a5client.ini")

def write_config(file_path : str = config_path, overwrite : bool = False, raise_if_exists : bool = False):
    config = configparser.ConfigParser()
    config.add_section("log")
    config.set("log","filename",defaults["log"]["filename"])
    if os.path.exists(file_path) and overwrite is False:
        if raise_if_exists:
            raise ValueError("Config file already exists")
    else:
        config.write(open(file_path,"w"))

def read_config(file_path : str = config_path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if os.path.exists(file_path):
        config.read(file_path)
    else:
        config.add_section("log")
        config.set("log","filename",defaults["log"]["filename"])

    # # Access sections and options
    # for section in config.sections():
    #     print(f"Section: {section}")
    #     for option in config.options(section):
    #         value = config.get(section, option)
    #         print(f"  {option} = {value}")

    return config

config = read_config()
