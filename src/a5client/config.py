api_url = "https://alerta.ina.gob.ar/a5"
api_token = None
proxy_dict = {
    "http": None,
    "https": None,
    "ftp": None
}
import os
appdir = "%s/.a5client" % os.environ["HOME"]
datadir = "%s/data" % appdir
logfile = "%s/a5client.log" % appdir