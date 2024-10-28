# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/29 13:26
@Author ： eblis
@File ：configurationCall.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/26 23:23
@Author ： eblis
@File ：configurationCall.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import configparser as cparser


################################# 配置文件的地址 ######################

conf_file_path = bae_idr + "/backendServices/config/config.ini"
conf = cparser.ConfigParser()
conf.read(conf_file_path, encoding="utf-8-sig")

###################################### switch ######################################

isClient = conf.get("switch", "isClient")

###################################### mysql 信息 ######################################

mysql_65_account = conf.get("mysql", "mysql_65_account")
mysql_65_password = conf.get("mysql", "mysql_65_password")
mysql_65_host = conf.get("mysql", "mysql_65_host")
mysql_65_port = conf.get("mysql", "mysql_65_port")
mysql_base_database = conf.get("mysql", "mysql_base_database")

mysql_111_account = conf.get("mysql", "mysql_111_account")
mysql_111_password = conf.get("mysql", "mysql_111_password")
mysql_111_host = conf.get("mysql", "mysql_111_host")
mysql_111_port = conf.get("mysql", "mysql_111_port")
mysql_article_database = conf.get("mysql", "mysql_article_database")

###################################### monggdb 信息 ######################################

mg_65_account = conf.get("mongodb", "mg_65_account")
mg_65_password = conf.get("mongodb", "mg_65_password")
mg_65_host = conf.get("mongodb", "mg_65_host")
mg_65_port = conf.get("mongodb", "mg_65_port")
mg_65_interim_databas = conf.get("mongodb", "mg_65_interim_databas")

###################################### jwt ######################################

jwt_secret_key = conf.get("jwt", "jwt_secret_key")
jwt_refresh_key = conf.get("jwt", "jwt_refresh_key")
expires_minutes = conf.get("jwt", "expires_minutes")

###################################### yescaptcha 信息 ######################################

ye_clientKey = conf.get("yescaptcha", "ye_clientKey")
ye_createTask = conf.get("yescaptcha", "ye_createTask")
ye_getTaskResult = conf.get("yescaptcha", "ye_getTaskResult")

###################################### flask 信息 ######################################

flaskport = conf.get("flask", "flaskport")
fixed_salt = conf.get("flask", "fixed_salt")
crossDomain = conf.get("flask", "crossDomain")

###################################### logs ######################################

log_folder_path = conf.get("logs", "log_folder_path")
log_folder_name = conf.get("logs", "log_folder_name")
log_level = conf.get("logs", "log_level")


###################################### Client ######################################

client_id = conf.get("Client", "client_id")

###################################### chromedriver 信息 ######################################
driverpath = conf.get("chromedriver", "chromedriverpath")
ye_plug_in = conf.get("chromedriver", "ye_plug_in")
userAgent = conf.get("chromedriver", "userAgent")
userDataDir = conf.get("chromedriver", "userDataDir")

###################################### amazon 信息 ######################################
aws_access_key = conf.get("amazon", "aws_access_key")
aws_secret_key = conf.get("amazon", "aws_secret_key")
aws_region_name = conf.get("amazon", "aws_region_name")
aws_policy_document = conf.get("amazon", "aws_policy_document")
task_address = conf.get("amazon", "task_address")


###################################### ads ######################################

adsServer = conf.get("ads", "adsServer")
telegra_ads = conf.get("ads", "telegra_ads")
min_concurrent_user = conf.get("ads", "min_concurrent_user")

###################################### telegra ######################################

stacking_text = conf.get("telegra", "stacking_text")
stacking_min = conf.get("telegra", "stacking_min")
stacking_max = conf.get("telegra", "stacking_max")
max_limit = conf.get("telegra", "max_limit")
telegra_result = conf.get("telegra", "telegra_result")

###################################### ahrefs ######################################

ahrefs_api_token = conf.get("ahrefs", "ahrefs_api_token")
ahrefs_base_url = conf.get("ahrefs", "ahrefs_base_url")

###################################### proxy ######################################

proxy_add = conf.get("proxy", "proxy_add")

###################################### other ######################################

temp_file_path = conf.get("other", "temp_file_path")






