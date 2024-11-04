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

    ############################################# splicing #####################################################


    # 批量插入
    def splicing_interim_insert_batch(self, setname, dataList):
        """
            @Datetime ： 2024/10/19 16:18
            @Author ：eblis
            @Motto：批量插入数据库
        """
        sql_data = self.mosql.insert_data(self.seo_interim, setname, dataList)

        return sql_data

    def splicing_interim_find_max(self, setname, max):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mosql.find_data(self.seo_interim, setname, end=max)


        return sql_data

    def splicing_interim_findAll(self, setname, genre=None, platform=None, projection=None, start=None, end=None):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """
        query = {}
        if genre is not None:
            query['genre'] = genre
        if platform is not None:
            query['platform'] = platform


            # 调用 find_data 方法执行查询
        sql_datas = self.mosql.find_data(self.seo_interim, setname, query=query, projection=projection, start=start, end=end)
        # print("sql_datas",sql_datas)

        return sql_datas

    def splicing_interim_find_count(self, setname, genre=None, platform=None):
        """
            @Datetime ： 2024/10/28 17:10
            @Author ：eblis
            @Motto：查表总数
        """
        query = {}
        if genre is not None:
            query['genre'] = genre
        if platform is not None:
            query['platform'] = platform

        sql_datas = self.mosql.find_count(self.seo_interim, setname, query)

        return sql_datas



    def splicing_interim_delet(self, setname, query, multiple, clear_all):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：query 传字典
        """
        sql_data = self.mosql.delete_data(self.seo_interim, setname, query=query, multiple=multiple,  clear_all=clear_all)


        return sql_data




############################################# operations #################################################################

    def operations_hosts_find(self, setname, query=None, projection=None, find_one=False, start=None, end=None):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """


            # 调用 find_data 方法执行查询
        sql_datas = self.mosql.find_data(self.seo_interim, setname, query=query, projection=projection, find_one=find_one, start=start, end=end)
        # print("sql_datas",sql_datas)

        return sql_datas


    def operations_hosts_insert(self, setname, data):
        """
            @Datetime ： 2024/10/19 16:18
            @Author ：eblis
            @Motto： 插入单条，data用字典形式
        """
        sql_data = self.mosql.insert_data(self.seo_interim, setname, data)

        return sql_data

    def operations_hosts_update(self, setname, query, update):
        """
            @Datetime ： 2024/10/19 16:18
            @Author ：eblis
            @Motto： 插入单条，data用字典形式
        """
        sql_data = self.mosql.update_data(self.seo_interim, setname, query, update, update_operator='$set', multi=False)

        return sql_data



    def operations_hosts_delet(self, setname, query, multiple, clear_all):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：query 传字典
        """
        sql_data = self.mosql.delete_data(self.seo_interim, setname, query=query, multiple=multiple,  clear_all=clear_all)


        return sql_data

    ###################################


    def operations_tasks_find(self, setname, query=None, projection=None, find_one=False, start=None, end=None):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """


            # 调用 find_data 方法执行查询
        sql_datas = self.mosql.find_data(self.seo_interim, setname, query=query, projection=projection, find_one=find_one, start=start, end=end)
        # print("sql_datas",sql_datas)

        return sql_datas


    def operations_tasks_logs_find(self, setname, query=None, projection=None, find_one=False, start=None, end=None):
        """
            @Datetime ： 2024/10/20 16:06
            @Author ：eblis
            @Motto：简单描述用途
        """


            # 调用 find_data 方法执行查询
        sql_datas = self.mosql.find_data(self.seo_interim, setname, query=query, projection=projection, find_one=find_one, start=start, end=end)
        # print("sql_datas",sql_datas)

        return sql_datas
