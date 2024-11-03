# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/6/15 14:53
@Author ： eblis
@File ：adsManage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import time

import requests

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from backendServices.unit.drivers.driversMod import DriversUtil
from middleware.public.commonUse import otherUse


class adsDevice():
    def __init__(self):
        self.DU = DriversUtil()
        self.usego = otherUse()


    def basicEncapsulation(self, who, adsServer):

        time.sleep(5)

        whodata = self.chromeStartUp(who, adsServer)

        self.usego.sendlog("{}选手信息如下：{}".format(who, whodata))

        whodata_dict = self.usego.changeDict(whodata)
        self.usego.sendlog(f"转换结果:{type(whodata_dict)},{whodata_dict}")
        try:
            chromedriver = whodata_dict["chromedriver"]
            if chromedriver != '':
                try:
                    driver = self.DU.drivers(driverpath=whodata_dict['chromedriver'], debugUP=whodata_dict["debugD"])
                    return driver
                except Exception as e:
                    self.usego.sendlog(f"ads接口 返回异常:{e}")
                    return False
            else:
                self.usego.sendlog("这个用户{},通过{} 启动chromeStartUp失败".format(who, adsServer))
                return False
        except Exception as e:
            self.usego.sendlog(f"{who}转换结果:{type(whodata_dict)},{whodata_dict},{e}")
            return False


    def chromeStartUp(self, userid, adsServer):
        asdchrome = {}
        response = self.adsAPI(adsServer, "start", userid)
        dict_response = self.usego.changeDict(response)
        self.usego.sendlog(f"本次请求结果:{dict_response}")
        try:
            asdchrome["chromedriver"] = dict_response['data'].get('webdriver')
            ws = dict_response['data']['ws']
            asdchrome["debugD"] = ws.get('selenium')
            return asdchrome
        except Exception as e:
            self.usego.sendlog(f"出现了异常{e}")
            return False




    def adsAPI(self, adsServer, mo, userid):

        self.usego.sendlog(f"准备执行：{mo}")
        if mo == "start":
            apiUrl = "/api/v1/browser/start?user_id={}".format(userid)
        else:
            apiUrl = "/api/v1/browser/stop?user_id={}".format(userid)
        url = adsServer + apiUrl
        headers = {'Content-Type': 'application/json'}
        self.usego.sendlog(f"当前访问: {url}")
        try:
            response = requests.get(url=url, headers=headers).json()
            return response
        except Exception as e:
            self.usego.sendlog(f"请求ADS 服务器失败: {e}")
            return False

