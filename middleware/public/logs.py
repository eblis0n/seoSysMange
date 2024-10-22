# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/3/4 19:47
@Author ： eblis
@File ：logs.py.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import re
import sys
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


from middleware.public.commonUse import otherUse


def log_config(folder_path, foldername, loglevel):
    usego = otherUse()

    log_path = usego.make_folder(folder_path, foldername)


    if loglevel == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif loglevel == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif loglevel == "WARNING":
        logging.basicConfig(level=logging.WARNING)
    elif loglevel == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    todaydate = datetime.now().strftime("%Y-%m-%d")
    log_file_path = log_path + "/" + todaydate + ".log"

    file_handler = TimedRotatingFileHandler(
        filename=log_file_path, when="MIDNIGHT", interval=1, backupCount=31, encoding="utf-8"
    )
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"))

    logger = logging.getLogger()
    logger.addHandler(file_handler)

    return logger




if __name__ == '__main__':
    # path = configuration.log_folder_path
    # name = configuration.log_folder_name
    # log_config(path, name, logging.DEBUG)
    pass