from setuptools import setup

setup(name='a5client',
      version='0.1',
      description='a5 api client',
      url='http://github.com/jbianchi81/a5client',
      author='SSIyAH-INA',
      author_email='jbianchi@ina.gob.ar',
      license='MIT',
      packages=['a5client'],
      install_requires=[
          'pandas',
          'jsonschema',
          'requests',
          'datetime',
          'pyyaml'
      ],
      zip_safe=False)

import os
import shutil
import a5client.config as config
isExist = os.path.exists(config.appdir)
if not isExist:
    os.mkdir(config.appdir)
isExist = os.path.exists(config.datadir)
if not isExist:
    os.mkdir(config.datadir)
shutil.copytree("data",config.datadir, dirs_exist_ok=True)
with open(config.logfile,"w") as create_log_file:
    pass