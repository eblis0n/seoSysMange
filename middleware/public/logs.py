import os
import re
import sys
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

def make_folder(path, name=None):
    """简化版的文件夹创建函数"""
    folder_path = os.path.join(path, name) if name else path
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"{folder_path} created successfully.")
    return folder_path

def make_file(path):
    """简化版的文件创建函数"""
    if not os.path.isfile(path):
        open(path, 'w').close()
        print(f"File {path} created successfully.")
    return path

def log_config(folder_path, foldername, loglevel="INFO"):
    """配置日志系统"""
    # 创建日志目录
    log_path = make_folder(folder_path, foldername)

    # 设置日志级别
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    logging.basicConfig(level=log_levels.get(loglevel, logging.INFO))

    # 创建日志文件
    todaydate = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_path, f"{todaydate}.log")
    today_log = make_file(log_file_path)

    # 配置文件处理器
    file_handler = TimedRotatingFileHandler(
        filename=today_log,
        when="MIDNIGHT",
        interval=1,
        backupCount=31,
        encoding="utf-8"
    )
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(lineno)s - %(message)s")
    )

    # 获取根日志记录器并添加处理器
    logger = logging.getLogger()
    logger.addHandler(file_handler)

    return logger