import os
import shutil
import src.a5client.config as config
isExist = os.path.exists(config.appdir)
if not isExist:
    os.mkdir(config.appdir)
isExist = os.path.exists(config.datadir)
if not isExist:
    os.mkdir(config.datadir)
shutil.copytree("data",config.datadir, dirs_exist_ok=True)
with open(config.logfile,"w") as create_log_file:
    pass