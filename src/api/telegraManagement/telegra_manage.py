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
import middleware.public.configurationCall as configCall
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.socialPlatforms.telegraGO.telegraSelenium import telegraSelenium



class telegraGO():
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
        print("sql_data", sql_data)
        if "sql 语句异常" not in str(sql_data):
            print("sql_data",sql_data)
            # try:
            #     resdatas = [{'id': item[0], 'salesperson': item[1], 'name': item[2],
            #                  'create_at': self.usego.turn_isoformat(item[3]),
            #                  'update_at': self.usego.turn_isoformat(item[4])} for item in sql_data]
            #
            # except:
            #     self.usego.sendlog(f'list没数据：{sql_data}')
            #     res = ResMsg(code='B0001', msg=f'list没数据：{sql_data}')
            #     responseData = res.to_json()
            # else:
            #     self.usego.sendlog(f'list结果：{resdatas}')
            #     res = ResMsg(data=resdatas)
            #     responseData = res.to_dict()

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

        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post")
        print("sql_data", sql_data)



        # self.tele.run(stacking_min, stacking_max, alt_tex)
        res = ResMsg(data=sql_data)
        responseData = res.to_json()
        return responseData




    