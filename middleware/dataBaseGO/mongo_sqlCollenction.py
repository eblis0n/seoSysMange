'''
version: 1.0.0
Author: Eblis
Date: 2024-10-19 13:30:51
LastEditTime: 2024-10-22 19:59:40
'''
# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 13:30
@Author ： eblis
@File ：mongo_sqlCollenction.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from backendServices.unit.dataBase.mongoDataBase import MongoDB
import middleware.public.configurationCall as configCall

# 执行后不主动关闭数据库连接，通过 外部调用 关闭
class mongo_sqlGO():
    def __init__(self):
        self.mosql = MongoDB()
        self.seo_interim = configCall.mg_65_interim_databas

    ############################################# 公共 #####################################################

    ############################################# telegra #####################################################


    # 批量插入
    def telegra_interim_insert_batch(self, setname, dataList):
        """
            @Datetime ： 2024/10/19 16:18
            @Author ：eblis
            @Motto：批量插入数据库
        """
        sql_data = self.mosql.insert_data(self.seo_interim, setname, dataList)

        return sql_data

    def telegra_interim_find_max(self, setname, max):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mosql.find_data(self.seo_interim, setname, limit=max)


        return sql_data

    def telegra_interim_findAll(self, setname):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mosql.find_data(self.seo_interim, setname)


        return sql_data


    def telegra_interim_multiple_delet(self, setname, query):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：query 传字典
        """
        sql_data = self.mosql.delete_data(self.seo_interim, setname, query, multiple=True)


        return sql_data







