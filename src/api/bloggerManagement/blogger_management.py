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


class bloggerManage():
    def __init__(self):
        self.bp = Blueprint("blogger", __name__, url_prefix="/blog")
        self.Myenum = MyEnum()

        self.ssql = basis_sqlGO()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.BLOGGER_INFO_INSERT, methods=['POST'])(self.blogger_info_insert)
        self.bp.route(self.Myenum.BLOGGER_INFO_DELETE, methods=['POST'])(self.blogger_info_delete)
        self.bp.route(self.Myenum.BLOGGER_INFO_UPDATE, methods=['POST'])(self.blogger_info_update)
        self.bp.route(self.Myenum.BLOGGER_INFO_LIST, methods=['GET'])(self.blogger_info_list)


    def blogger_info_insert(self):

        data_request = request.json
        group = data_request['group']
        adsNumber = data_request['adsNumber']
        adsID = data_request['adsID']
        proxy = data_request['proxy']
        bloggerID = data_request['bloggerID']
        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print("proxy",proxy)


        sql_data = self.ssql.blogger_info_insert_sql(group, adsNumber, adsID, proxy, bloggerID, create_at)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()



    def blogger_info_delete(self):

        data_request = request.json
        id = data_request['id']


        sql_data = self.ssql.blogger_info_delete_sql(id)
        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def blogger_info_update(self):

        data_request = request.json
        id = data_request['id']
        group = data_request['group']
        adsNumber = data_request['adsNumber']
        adsID = data_request['adsID']
        proxy = data_request['proxy']
        bloggerID = data_request['bloggerID']



        sql_data = self.ssql.blogger_info_update_sql(group, adsNumber, adsID, proxy, bloggerID, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)


        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')

        return res.to_json()

    def blogger_info_list(self):
        sql_data = self.ssql.blogger_info_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [
                    {'id': item[0], 'group': item[1], 'adsNumber': item[2], 'adsID': item[3],  'proxy': item[4], 'bloggerID': item[5],
                     'create_at': self.usego.turn_isoformat(item[6]), 'update_at': self.usego.turn_isoformat(item[7])} for
                    item in sql_data]


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

