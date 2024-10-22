# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 16:31
@Author ： eblis
@File ：telegra_manage.py
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



class telegraManage():
    def __init__(self):
        self.bp = Blueprint("telegra", __name__, url_prefix="/telegra")
        self.mossql = mongo_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.tele = telegraSelenium()


        self.bp.route(self.Myenum.SUBMIT_301, methods=['POST'])(self.submit_301)
        self.bp.route(self.Myenum.SPLICING_LIST, methods=['GET'])(self.splicing_list)
        
    def splicing_list(self):
        """
            @Datetime ： 2024/10/21 00:28
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post")
        resdatas = []
        # print("sql_data", sql_data)
        if "sql 语句异常" not in str(sql_data):
            try:
                for i, data in sql_data:
                    thisdata = {
                        "id": i,
                        "url": data["url"],
                        "created_at": self.usego.turn_isoformat(data["created_at"])
                    }
                    resdatas.append(thisdata)

            except Exception as e:
                print(f"{e}")
                self.usego.sendlog(f'list没数据：{sql_data}')
                res = ResMsg(code='B0001', msg=f'list没数据：{sql_data}')
                responseData = res.to_json()
            else:
                self.usego.sendlog(f'list结果：{resdatas}')
                res = ResMsg(data=resdatas)
                responseData = res.to_json()

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败：{sql_data}')
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

