# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/12 13:30
@Author ： eblis
@File ：script_template_manage.py
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

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse

class scriptTemplateManage:
    def __init__(self):
        self.bp = Blueprint("scriptTemplate", __name__, url_prefix="/template")
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.SCRIPT_TEMPLATE_INSERT, methods=['POST'])(self.script_template_insert)
        self.bp.route(self.Myenum.SCRIPT_TEMPLATE_DELETE, methods=['POST'])(self.script_template_delete)
        self.bp.route(self.Myenum.SCRIPT_TEMPLATE_UPDATE, methods=['POST'])(self.script_template_update)
        self.bp.route(self.Myenum.SCRIPT_TEMPLATE_LIST, methods=['GET'])(self.script_template_list)


    def script_template_insert(self):

        data_request = request.json
        script_type = data_request['script_type']
        script_name = data_request['script_name']
        script_content = data_request['script_content']
        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            script_content_str = json.dumps(script_content)
        except:
            script_content_str = str(script_content).replace("'", '"')


        sql_data = self.ssql.script_template_insert_sql(script_name, script_type, script_content_str, create_at )

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()



    def script_template_delete(self):

        data_request = request.json
        id = data_request['id']

        sql_data = self.ssql.script_template_delete_sql(id)
        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)


        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def script_template_update(self):

        data_request = request.json
        id = data_request['id']
        script_type = data_request['script_type']
        script_name = data_request['script_name']
        script_content = data_request['script_content']


        sql_data = self.ssql.script_template_update_sql(script_name, script_type, script_content, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')

        return res.to_json()

    def script_template_list(self):
        sql_data = self.ssql.script_template_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0],
                             'script_type': item[1],
                             'script_name': item[2],
                             'script_content': item[3],
                             'create_at': self.usego.turn_isoformat(item[4]),
                             'update_at': self.usego.turn_isoformat(item[5])
                             } for item in sql_data]

            except:
                self.usego.sendlog(f'list没数据：{sql_data}')
                res = ResMsg(code='B0001', msg=f'list没数据：{sql_data}')

            else:
                self.usego.sendlog(f'list结果：{resdatas}')
                res = ResMsg(data=resdatas)


        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败：{sql_data}')


        return res.to_json()