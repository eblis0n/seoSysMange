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
import time

from pymongo import MongoClient
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse

# 设置项目根目录
base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


class MongoDB:
    def __init__(self):
        self.usego = otherUse()
        self.client = None  # 初始化时不连接
        self.host = configCall.mg_65_host
        self.port = eval(configCall.mg_65_port)
        self.username = configCall.mg_65_account
        self.password = configCall.mg_65_password

    def connect(self):
        """连接到 MongoDB 数据库"""
        if self.client is None:  # 仅在第一次调用时连接
            base_url = f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}'
            try:
                self.client = MongoClient(base_url, maxPoolSize=50, minPoolSize=10, connectTimeoutMS=120000, socketTimeoutMS=120000)
            except:
                self.usego.sendlog(f"连接失败{base_url}")
                time.sleep(5)
                try:
                    self.client = MongoClient(base_url, maxPoolSize=50, minPoolSize=10, connectTimeoutMS=120000, socketTimeoutMS=120000)
                except:
                    self.client = None



    def get_database(self, database_name):
        """获取指定数据库的连接"""
        self.connect()  # 确保连接
        return self.client[database_name]

    def mongo_connect(self, database_name):
        """连接到 MongoDB 并返回数据库对象"""
        try:
            self.connect()  # 确保连接
            db_list = self.client.list_database_names()  # 获取数据库列表
            if database_name in db_list:
                return self.get_database(database_name)
            else:
                self.usego.sendlog(f"连接成功！但数据库 '{database_name}' 不存在。")
                return None
        except Exception as e:
            self.usego.sendlog(f"连接失败: {e}")
            return None

    def get_collection(self, dbname, setname):
        """返回数据库集合对象（根据集合名称）"""
        db = self.mongo_connect(dbname)
        if db is not None:
            try:
                return db[setname]  # 获取集合
            except Exception as e:
                self.usego.sendlog(f"获取集合失败: {e}")
                return None
        return None

    def close(self):
        """关闭 MongoDB 连接"""
        if self.client:
            self.client.close()
            self.usego.sendlog("MongoDB 连接已关闭。")

    def find_data(self, dbname, setname, query=None, projection=None, find_one=False, limit=None):
        """通用查询方法"""
        mycol = self.get_collection(dbname, setname)
        if mycol is not None:
            try:
                if query is None:
                    query = {}
                if find_one:
                    return mycol.find_one(query, projection)  # 单条查询
                else:
                    result = mycol.find(query, projection)

                    if limit:
                        self.usego.sendlog(f"有数量限{limit}")
                        result = result.limit(limit)  # 设置返回结果的限制数量
                    return list(result)  # 查询全部
            except Exception as e:
                self.usego.sendlog(f"MongoDB 查询错误: {e}")
                return None
        return None

    def insert_data(self, dbname, setname, data):
        """插入数据到集合：支持单条插入和批量插入"""
        mycol = self.get_collection(dbname, setname)
        if mycol is not None:
            try:
                if isinstance(data, list):  # 批量插入
                    result = mycol.insert_many(data)
                    return result.inserted_ids
                else:  # 单条插入
                    result = mycol.insert_one(data)
                    return result.inserted_id
            except Exception as e:
                self.usego.sendlog(f"MongoDB 插入错误: {e}")
                return None
        return None

    def update_data(self, dbname, setname, query, update, update_operator='$set', multi=False):
        """更新集合中的单个或多个文档"""
        mycol = self.get_collection(dbname, setname)
        if mycol is not None:
            try:
                update_dict = {update_operator: update}
                if multi:  # 批量更新
                    result = mycol.update_many(query, update_dict)
                else:  # 单条更新
                    result = mycol.update_one(query, update_dict)
                return {
                    "acknowledged": result.acknowledged,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count
                }
            except Exception as e:
                self.usego.sendlog(f"MongoDB 更新错误: {e}")
                return None
        return None

    def delete_data(self, dbname, setname, query, multiple=False):
        """删除集合中的单个或多个文档"""
        mycol = self.get_collection(dbname, setname)
        if mycol is not None:
            try:
                if multiple:  # 批量删除
                    result = mycol.delete_many(query)
                else:  # 单条删除
                    result = mycol.delete_one(query)
                return {
                    "acknowledged": result.acknowledged,
                    "deleted_count": result.deleted_count
                }
            except Exception as e:
                self.usego.sendlog(f"MongoDB 删除错误: {e}")
                return None
        return None
