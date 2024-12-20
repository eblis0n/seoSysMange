# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/1/11 14:59
@Author ： eblis
@File ：pc_settings_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
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
        group = data_request['group']
        name = data_request['name']
        address = data_request['address']
        account = data_request['account']
        password = data_request['password']
        # platform = data_request['platform']
        remark = data_request['remark'].replace("\n", ',')
        try:
            platform = json.dumps(data_request['platform'])
        except:
            platform = str(data_request['platform']).replace("'", '"').replace('"', "'")


        sql_data = self.ssql.pcSettings_insert_sql(group, name, address, account, password, platform, remark, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
            responseData = res.to_json()

        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')
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
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')
            responseData = res.to_json()
        return responseData


    def pc_update(self):

        data_request = request.json
        state = data_request['state']
        id = data_request['id']
        group = data_request['group']
        name = data_request['name']
        address = data_request['address']
        account = data_request['account']
        password = data_request['password']
        remark = data_request['remark'].replace("\n", ',')
        # platform = data_request['platform']
        try:
            platform = json.dumps(data_request['platform'])
        except:
            platform = str(data_request['platform']).replace("'", '"').replace('"', "'")


        sql_data = self.ssql.pcSettings_update_sql(group, name, address, account, password, platform, remark, state, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)
            responseData = res.to_json()

        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')
            responseData = res.to_json()
        return responseData

    def pc_list(self):
        sql_data = self.ssql.pcSettings_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0],
                             'group': item[1],
                             'name': item[2],
                             'address': item[3],
                             'account': item[4],
                             'password': item[5],
                             'platform': item[6],
                             'state': item[7],
                              'remark': item[8],
                             'create_at': self.usego.turn_isoformat(item[9]),
                             'update_at': self.usego.turn_isoformat(item[10])
                             } for item in sql_data]

            except:
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

