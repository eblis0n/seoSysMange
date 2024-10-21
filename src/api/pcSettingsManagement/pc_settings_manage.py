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

from flask import Blueprint,request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse


class pcManage():
    def __init__(self):
        self.bp = Blueprint("pc", __name__, url_prefix="/client")
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.PC_INSERT, methods=['POST'])(self.pc_insert)
        self.bp.route(self.Myenum.PC_DELETE, methods=['POST'])(self.pc_delete)
        self.bp.route(self.Myenum.PC_UPDATE, methods=['POST'])(self.pc_update)
        self.bp.route(self.Myenum.PC_LIST, methods=['GET'])(self.pc_list)


    def pc_insert(self):

        data_request = request.json
        name = data_request['name']
        address = data_request['address']


        sql_data = self.ssql.pcSettings_insert_sql(name, address, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
            responseData = res.to_json()

        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code=10001, msg=f'添加失败：{sql_data}')
            responseData = res.to_json()
        return responseData



    def pc_delete(self):

        data_request = request.json
        id = data_request['id']

        sql_data = self.ssql.pcSettings_delete_sql(id)
        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)
            responseData = res.to_json()

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code=10001, msg=f'删除失败：{sql_data}')
            responseData = res.to_json()
        return responseData


    def pc_update(self):

        data_request = request.json
        name = data_request['name']
        address = data_request['address']
        state = data_request['state']
        id = data_request['id']


        sql_data = self.ssql.pcSettings_update_sql(name, address, state, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)
            responseData = res.to_json()

        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code=10001, msg=f'更新失败：{sql_data}')
            responseData = res.to_json()
        return responseData

    def pc_list(self):
        sql_data = self.ssql.pcSettings_list_sql()

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'name': item[1], 'address': item[2], 'state': item[3],
                             'create_at': self.usego.turn_isoformat(item[4]),
                             'update_at': self.usego.turn_isoformat(item[5])} for item in sql_data]

            except:
                self.usego.sendlog(f'list没数据：{sql_data}')
                res = ResMsg(code=10001, msg=f'list没数据：{sql_data}')
                responseData = res.to_json()
            else:
                self.usego.sendlog(f'list结果：{resdatas}')
                res = ResMsg(data=resdatas)
                responseData = res.to_json()

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code=10001, msg=f'list查询失败：{sql_data}')
            responseData = res.to_json()

        return responseData

