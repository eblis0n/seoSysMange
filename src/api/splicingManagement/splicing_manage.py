# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 16:31
@Author ： eblis
@File ：splicing_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from middleware.public.returnMsg import ResMsg

from flask import Blueprint, request
from src.api.urlSet import MyEnum

from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.socialPlatforms.telegraGO.telegraSelenium import telegraSelenium
from backendServices.src.assistance.spliceGo import spliceGo



class splicingManage():
    def __init__(self):
        self.bp = Blueprint("splicing", __name__, url_prefix="/splicing")
        self.mossql = mongo_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.tele = telegraSelenium()
        self.bp.route(self.Myenum.SUBMIT_301, methods=['POST'])(self.submit_301)

        self.bp.route(self.Myenum.SPLICING_SUPPORTED_PLATFORMS, methods=['GET'])(self.splicing_supported_platforms)
        self.bp.route(self.Myenum.SPLICING_INSERT, methods=['POST'])(self.splicing_insert)
        self.bp.route(self.Myenum.SPLICING_LIST, methods=['GET'])(self.splicing_list)
        
    def splicing_list(self):
        """
            @Datetime ： 2024/10/21 00:28
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post")
        resdatas = []
        print("sql_data", sql_data)
        if "sql 语句异常" not in str(sql_data):
            try:
                if len(sql_data) > 0:
                    for i in range(len(sql_data)):
                        thisdata = {
                            "id": i,
                            "url": sql_data[i]["url"],
                            "platform": sql_data[i]["platform"],
                            "genre": sql_data[i]["genre"],
                            "created_at": self.usego.turn_isoformat(sql_data[i]["created_at"])
                        }
                        resdatas.append(thisdata)

                    self.usego.sendlog(f'list结果：{resdatas}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
                else:
                    self.usego.sendlog(f'list结果：{resdatas}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
            except Exception as e:
                self.usego.sendlog(f'list查询失败：{e}')
                res = ResMsg(code='B0001', msg=f'list查询失败')
                responseData = res.to_json()
        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败')
            responseData = res.to_json()

        return responseData

    def splicing_insert(self):

        data_request = request.json
        zyurl = data_request['zyurl']
        url = data_request['url']
        genre = data_request['genre']
        platform = data_request['platform']

        zyurl_list = zyurl.split(",")
        url_list = url.split(",")
        spl = spliceGo()
        result = spl.splice_301(zyurl_list, url_list, platform, genre)
        if result is not None:
            self.usego.sendlog(f'添加成功：{result}')
            res = ResMsg(data=result)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'入库失败')
            res = ResMsg(code='B0001', msg=f'v')
            responseData = res.to_json()

        return responseData

    def splicing_supported_platforms(self):
        platforms = [
          {
            "value": "telegra",
            "label": "telegra",
          },
        ]
        res = ResMsg(data=platforms)
        responseData = res.to_json()

        return responseData
        
        
    def submit_301(self):
        """
            @Datetime ： 2024/10/19 17:12
            @Author ：eblis
            @Motto：简单描述用途
        """

        data_request = request.json
        stacking_min = data_request['stacking_min']
        stacking_max = data_request['stacking_max']
        alt_tex = data_request['alt_tex']
        print("进来了")

        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post")

        all_links = []
        for data in sql_data:

            all_links.append(data["url"])
        print(f"{len(all_links)}")

        self.tele.run(all_links, stacking_min, stacking_max, alt_tex)
        res = ResMsg(data=sql_data)
        responseData = res.to_json()
        return responseData

