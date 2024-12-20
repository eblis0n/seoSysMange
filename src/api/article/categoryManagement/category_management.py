# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/1/11 14:59
@Author ： eblis
@File ：pc_settings_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from datetime import datetime
from middleware.public.returnMsg import ResMsg

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.public.commonUse import otherUse


class categoryManage():
    def __init__(self):
        self.bp = Blueprint("category", __name__, url_prefix="/category")
        self.Myenum = MyEnum()

        self.artsql = article_sqlGO()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.CATEGORY_INSERT, methods=['POST'])(self.category_insert)
        self.bp.route(self.Myenum.CATEGORY_DELETE, methods=['POST'])(self.category_delete)
        self.bp.route(self.Myenum.CATEGORY_UPDATE, methods=['POST'])(self.category_update)
        self.bp.route(self.Myenum.CATEGORY_LIST, methods=['GET'])(self.category_list)

    def category_insert(self):

        data_request = request.json
        name = data_request['name']
        level = data_request['level']
        create_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql_data = self.artsql.category_insert_sql(name, level, create_at)


        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()

    def category_delete(self):

        data_request = request.json
        id = data_request['id']

        sql_data = self.artsql.category_delete_sql(id)
        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除:{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败:{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败:{sql_data}')

        return res.to_json()

    def category_update(self):

        data_request = request.json
        id = data_request['id']
        name = data_request['name']
        level = data_request('level')


        sql_data = self.artsql.category_update_sql(name, level, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功: {sql_data}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'更新失败: {sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败: {sql_data}')

        return res.to_json()

    def category_list(self):

        sql_data = self.artsql.category_list_sql()

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [
                    {'id': item[0], 'name': item[1], 'level': item[2], 'create_at': self.usego.turn_isoformat(item[3]),
                    'update_at': self.usego.turn_isoformat(item[4])}for item in sql_data]

            except:
                self.usego.sendlog(f'list没数据: {sql_data}')
                res = ResMsg(code='B0001', msg=f'list没数据: {sql_data}')

            else:
                self.usego.sendlog(f'list结果:{resdatas}')
                res = ResMsg(data=resdatas)

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败:{sql_data}')

        return res.to_json()