# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 13:37
@Author ： eblis
@File ：mongoDataBase.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
import middleware.public.configurationCall as configCall
from pymongo import MongoClient

class mongodb():
    def __init__(self):
        # 只在类实例化时创建一次 MongoClient，连接池会自动管理连接复用
        host = configCall.mg_65_host
        port = eval(configCall.mg_65_port)
        username = configCall.mg_65_account
        password = configCall.mg_65_password
        self.mongodb_url = f'mongodb://{username}:{password}@{host}:{port}'
        self.client = MongoClient(self.mongodb_url, maxPoolSize=50, minPoolSize=5)

    def mongo_65_connect(self, databaseName):
        '''
        连接到 MongoDB 并返回数据库对象
        '''
        try:
            # 获取数据库列表
            db_list = self.client.list_database_names()

            # 检查数据库是否存在
            if databaseName in db_list:
                db = self.client[databaseName]
                return db
            else:
                print(f"连接成功！但数据库 '{databaseName}' 不存在。")
                return False
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def mongocol(self, dbname, setname):
        '''
        返回数据库集合对象（根据集合名称）
        '''
        db = self.mongo_65_connect(dbname)
        if db:
            try:
                setgo = db[setname]
                return setgo
            except Exception as e:
                print(f"获取集合失败: {e}")
                return False
        return False


    def close(self):
        '''
        关闭 MongoDB 连接
        '''
        if self.client:
            self.client.close()
            print("MongoDB 连接已关闭。")


    ##############################################封装执行方法#################################################

    def find_data(self, dbname, setname, query=None, projection=None, find_one=False):
        '''
        通用查询方法，支持单条查询、查询全部以及带查询条件的查询
        :param dbname: 数据库名称
        :param setname: 集合名称
        :param query: 查询条件，默认为空字典 {}，表示查询全部
        :param projection: 返回字段的筛选条件，默认为 None，返回全部字段
        :param find_one: 是否只查询单条，默认为 False；如果为 True，则只返回第一条匹配的记录
        :return: 查询结果，单条记录返回字典，多条记录返回列表
        '''
        mycol = self.mongocol(dbname, setname)
        if mycol:
            try:
                # 如果没有提供查询条件，则默认查询所有记录
                if query is None:
                    query = {}
                # 单条查询
                if find_one:
                    result = mycol.find_one(query, projection)
                    return result
                # 查询全部（或指定条件的多条查询）
                else:
                    result = mycol.find(query, projection)
                    result_list = list(result)
                    return result_list
            except Exception as e:
                print(f"MongoDB query error: {e}")
                return False
        return False


    def insert_data(self, dbname, setname, data):
        '''
        插入数据到集合：支持单条插入和批量插入
        :param dbname: 数据库名称
        :param setname: 集合名称
        :param data: 可以是单个字典或字典列表
        :return: 插入后的文档ID或ID列表
        '''
        mycol = self.mongocol(dbname, setname)
        if mycol:
            try:
                if isinstance(data, list):  # 判断是否为批量插入
                    result = mycol.insert_many(data)
                    return result.inserted_ids
                else:  # 单条插入
                    result = mycol.insert_one(data)
                    return result.inserted_id
            except Exception as e:
                print(f"MongoDB insert error: {e}")
                return False
        return False


    def updat_data(self, dbname, setname, query, update, update_operator='$set', multi=False):
        '''
        更新集合中的单个或多个文档
        :param dbname: 数据库名称
        :param setname: 集合名称
        :param query: 查询条件，单条更新时为字典，批量更新时也为字典
        :param update: 更新内容，字典形式
        :param update_operator: 更新操作符，默认为 '$set'，可以根据需求传入其他更新操作符
        :param multi: 是否为批量更新，默认为 False（单条更新），为 True 时执行批量更新
        :return: 返回更新操作的结果，包括是否成功、匹配的文档数和修改的文档数
        '''
        mycol = self.mongocol(dbname, setname)
        if mycol:
            try:
                # 使用动态更新操作符
                update_dick = {update_operator: update}

                if multi:  # 如果是批量更新
                    result = mycol.update_many(query, update_dick)
                else:  # 单条更新
                    result = mycol.update_one(query, update_dick)

                # 返回更多信息：操作是否成功、匹配的文档数和修改的文档数
                return {
                    "acknowledged": result.acknowledged,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count
                }
            except Exception as e:
                print(f"MongoDB query error: {e}")
                return False
        return False

    def delet_data(self, dbname, setname, query, multiple=False):
        '''
        删除集合中的单个或多个文档
        :param dbname: 数据库名称
        :param setname: 集合名称
        :param query: 查询条件，单条删除时为字典，批量删除时为字典
        :param multiple: 是否为批量删除，默认为 False（单条删除），为 True 时执行批量删除
        :return: 返回删除操作的结果，包括是否成功、删除的文档数
        '''
        mycol = self.mongocol(dbname, setname)
        if mycol:
            try:
                if multiple:  # 如果是批量删除
                    result = mycol.delete_many(query)
                else:  # 单条删除
                    result = mycol.delete_one(query)

                # 返回删除结果
                return {
                    "acknowledged": result.acknowledged,
                    "deleted_count": result.deleted_count
                }
            except Exception as e:
                print(f"MongoDB delete error: {e}")
                return False
        return False




    