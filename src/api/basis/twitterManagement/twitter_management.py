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
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse


class twitterManage():
    def __init__(self):
        self.bp = Blueprint("twitter", __name__, url_prefix="/tw")
        self.Myenum = MyEnum()

        self.ssql = basis_sqlGO()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.TWITTER_INFO_INSERT, methods=['POST'])(self.twitter_info_insert)
        self.bp.route(self.Myenum.TWITTER_INFO_DELETE, methods=['POST'])(self.twitter_info_delete)
        self.bp.route(self.Myenum.TWITTER_INFO_UPDATE, methods=['POST'])(self.twitter_info_update)
        self.bp.route(self.Myenum.TWITTER_INFO_LIST, methods=['GET'])(self.twitter_info_list)


    def twitter_info_insert(self):

        data_request = request.json
        group = data_request['group']
        adsNumber = data_request['adsNumber']
        adsID = data_request['adsID']
        proxy = data_request['proxy']
        twuser = data_request['twuser']
        twpassword = data_request['twpassword']
        email = data_request['email']
        emailPwd = data_request['emailPwd']
        auth_token = data_request['auth_token']
        cookie = data_request['cookie']
        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")



        sql_data = self.ssql.twitter_info_insert_sql(group, adsNumber, adsID, proxy, twuser, twpassword, email, emailPwd, auth_token, cookie, create_at)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()



    def twitter_info_delete(self):

        data_request = request.json
        id = data_request['id']


        sql_data = self.ssql.twitter_info_delete_sql(id)
        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def twitter_info_update(self):

        data_request = request.json
        id = data_request['id']
        group = data_request['group']
        adsNumber = data_request['adsNumber']
        adsID = data_request['adsID']
        proxy = data_request['proxy']
        twuser = data_request['twuser']
        twpassword = data_request['twpassword']
        email = data_request['email']
        emailPwd = data_request['emailPwd']
        auth_token = data_request['auth_token']
        cookie = data_request['cookie']



        sql_data = self.ssql.twitter_info_update_sql(group, adsNumber, adsID, proxy, twuser, twpassword, email, emailPwd, auth_token, cookie, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)


        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')

        return res.to_json()

    def twitter_info_list(self):
        sql_data = self.ssql.twitter_info_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [
                    {'id': item[0], 'group': item[1], 'adsNumber': item[2], 'adsID': item[3],  'proxy': item[4], 'twuser': item[5],
                     'twpassword': item[6], 'email': item[7], 'emailPwd': item[8], 'auth_token': item[9], 'cookie': item[10], 'create_at': self.usego.turn_isoformat(item[11]), 'update_at': self.usego.turn_isoformat(item[12])} for
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

