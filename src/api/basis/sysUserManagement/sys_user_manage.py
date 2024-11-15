# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/26 23:45
@Author ： eblis
@File ：sys_menu_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys


base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.public.returnMsg import ResMsg

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse
from middleware.jwtGO.py_jwt import get_new_token, destroy_token, get_verify_token


class userService():
    def __init__(self):
        self.bp = Blueprint("sysUser", __name__, url_prefix="/sys/user")
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.SYS_USER_LOGOUT, methods=['DELETE'])(self.sys_user_logout)
        self.bp.route(self.Myenum.SYS_USER_LOGIN, methods=['POST'])(self.sys_user_login)
        self.bp.route(self.Myenum.SYS_USER_LIST, methods=['GET'])(self.sys_user_list)
        self.bp.route(self.Myenum.SYS_USER_INFO, methods=['GET'])(self.sys_user_info)

    def sys_user_list(self):
        """
            @Datetime ： 2024/9/27 00:00
            @Author ：eblis
            @Motto：管理后台用户管理
        """

        sql_data = self.ssql.sys_user_list()
        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'salesperson': item[1], 'name': item[2],
                             'create_at': self.usego.turn_isoformat(item[3]),
                             'update_at': self.usego.turn_isoformat(item[4])} for item in sql_data]

            except:
                self.usego.sendlog(f'list没数据：{sql_data}')
                res = ResMsg(code='B0001', msg=f'list没数据：{sql_data}')
                responseData = res.to_json()
            else:
                self.usego.sendlog(f'list结果：{resdatas}')
                res = ResMsg(data=resdatas)
                responseData = res.to_dict()

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败：{sql_data}')
            responseData = res.to_json()


        return responseData

    # def sys_user_login(self):
    #     form_data = request.json
    #     username = form_data['username']
    #     password = form_data['password']
    #
    #     pwd = self.usego.change_hashed(password)
    #
    #
    #     sql_data = self.ssql.sys_user_info_select(username=username, password=pwd)
    #
    #     if "sql 语句异常" not in str(sql_data):
    #         try:
    #             resdatas = [{'id': item[0], 'username': item[1], 'nickname': item[2], 'gender': item[3],
    #                          'password': item[4], 'dept_id': item[5], 'avatar': item[6], 'mobile': item[7],
    #                          'status': item[8], 'email': item[9],
    #                          'create_at': self.usego.turn_isoformat(item[10]),
    #                          'create_by': self.usego.turn_isoformat(item[11]),
    #                          'update_at': self.usego.turn_isoformat(item[12]),
    #                          'update_by': self.usego.turn_isoformat(item[13])} for item in sql_data]
    #
    #
    #         except:
    #             self.usego.sendlog(f'请检查账号/密码是否正确：{sql_data}')
    #             res = ResMsg(code='B0001', msg=f'请检查账号/密码是否正确')
    #             responseData = res.to_json()
    #
    #             return responseData
    #         else:
    #             # print("resdatas", resdatas)
    #             if resdatas !=[]:
    #                 try:
    #                     datas = get_new_token(resdatas[0]["id"])
    #                 except:
    #                     self.usego.sendlog(f'请检查账号/密码是否正确：{sql_data}')
    #                     res = ResMsg(code='B0001', msg=f'请检查账号/密码是否正确')
    #                     responseData = res.to_json()
    #
    #                     return responseData
    #                 else:
    #
    #                     res = ResMsg(data=datas)
    #                     responseData = res.to_json()
    #
    #                     return responseData
    #     else:
    #         self.usego.sendlog(f'请检查账号/密码是否正确：{sql_data}')
    #         res = ResMsg(code='B0001', msg=f'请检查账号/密码是否正确')
    #         responseData = res.to_json()
    #
    #         return responseData


    # def sys_user_info(self):
    #
    #     user_id = get_verify_token()
    #     print("user_id",user_id)
    #     sql_data = self.ssql.sys_user_perm_select(user_id=user_id)
    #
    #
    #     if "sql 语句异常" not in str(sql_data):
    #         try:
    #             resdatas = [{'user_id': item[0], 'username': item[1], 'nickname': item[2], 'avatar': item[3],
    #                          'role': item[4], 'perm': item[5]} for item in sql_data]
    #
    #         except:
    #             self.usego.sendlog(f'请检查账号/密码是否正确：{sql_data}')
    #             res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
    #             responseData = res.to_json()
    #
    #             return responseData
    #         else:
    #             if resdatas != []:
    #                 # print("resdatas",resdatas)
    #
    #                 roles = []
    #                 perms = []
    #                 for i in range(len(resdatas)):
    #
    #                     if resdatas[i]['perm'] not in perms:
    #                         perms.append(resdatas[i]['perm'])
    #                     if resdatas[i]['role'] not in roles:
    #                         roles.append(resdatas[i]['role'])
    #
    #                 user_info = {
    #                     "userId": resdatas[0]['user_id'],
    #                     "username": resdatas[0]['username'],
    #                     "avatar": resdatas[0]['avatar'],
    #                     "roles": roles,
    #                     "perms": perms,
    #                 }
    #
    #                 self.usego.sendlog(f'用户信息结果：{user_info}')
    #                 res = ResMsg(data=user_info)
    #                 responseData = res.to_json()
    #
    #             else:
    #                 self.usego.sendlog(f'查无此用户，请查正后再重试')
    #                 res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
    #                 responseData = res.to_json()
    #
    #             return responseData
    #
    #     else:
    #         self.usego.sendlog(f'查无此用户，请查正后再重试')
    #         res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
    #         responseData = res.to_json()
    #
    #         return responseData

    def sys_user_logout(self):

        result = destroy_token()

        self.usego.sendlog(f'退出登录：{result}')
        res = ResMsg()
        responseData = res.to_json()
        return responseData






    # ######################################## 调试 #####################################################################
    def sys_user_login(self):
        form_data = request.json
        username = form_data['username']
        password = form_data['password']
        print(f"当前登录用户{username},{password}")
        datas = get_new_token(2)

        res = ResMsg(data=datas)
        responseData = res.to_json()

        return responseData


    def sys_user_info(self):

        user_info = {
            "userId": 2,
            "username": "admin",
            "avatar": "https://oss.youlai.tech/youlai-boot/2023/05/16/811270ef31f548af9cffc026dfc3777b.gif",
            "roles": [
                "\u7cfb\u7edf\u7ba1\u7406\u5458"
            ],
            "perms": [
                "sys:user:add",
                "sys:user:edit",
                "sys:user:delete",
                "sys:user:password:reset",
                "sys:user:query",
                "sys:user:import",
                "sys:user:export",
                "sys:role:add",
                "sys:role:edit",
                "sys:role:delete",
                "sys:menu:add",
                "sys:menu:edit",
                "sys:menu:delete",
                "sys:dept:add",
                "sys:dept:edit",
                "sys:dept:delete",
                "sys:dict_type:add",
                "sys:dict_type:edit",
                "sys:dict_type:delete",
                "sys:dict:add",
                "sys:dict:edit",
                "sys:dict:delete"
            ]
        }

        res = ResMsg(data=user_info)
        responseData = res.to_json()

        return responseData








