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
import time

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.public.returnMsg import ResMsg

from flask import Blueprint
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse
from middleware.jwtGO.py_jwt import get_verify_token


class menuDeploy():
    def __init__(self):
        self.bp = Blueprint("menuDeploy", __name__, url_prefix="/sys/menu")
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        # self.bp.route(self.Myenum.SYS_USER_LOGOUT, methods=['DELETE'])(self.sys_user_logout)
        # self.bp.route(self.Myenum.SYS_USER_LOGIN, methods=['POST'])(self.sys_user_login)
        # self.bp.route(self.Myenum.SYS_USER_LIST, methods=['GET'])(self.sys_user_list)
        self.bp.route(self.Myenum.SYS_MENU_ROUTES, methods=['GET'])(self.sys_menu_routes)

    def sys_menu_routes(self):
        """
            @Datetime ： 2024/9/27 00:00
            @Author ：eblis
            @Motto：管理后台用户管理
        """
        user_id = get_verify_token()
        # print("user_id",user_id)
        sql_data = self.ssql.sys_user_router_code_select(user_id)
        # print("sql_data",sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                router_code = [item[0] for item in sql_data]

            except:
                self.usego.sendlog(f'查无此数据：{sql_data}')
                res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
                responseData = res.to_json()

                return responseData
            else:
                self.usego.sendlog(f'router_code：{router_code}')
                time.sleep(5)
                sql_data = self.ssql.menu_router_list(router_code, 4)
                # print("sql_data",sql_data)
                if "sql 语句异常" not in str(sql_data):
                    try:
                        resdatas = [{'id': item[0], 'name': item[1], 'parent_id': item[2], 'route_name': item[3],
                                     'route_path': item[4], 'component': item[5], 'icon': item[6], 'sort': item[7], 'visible': item[8], 'redirect': item[9], 'type': item[10], 'always_show': item[11], 'keep_alive': item[12], 'params': item[13]} for item in sql_data]

                    except:
                        self.usego.sendlog(f'菜单查询失败：{sql_data}')
                        res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
                        responseData = res.to_json()

                        return responseData
                    else:
                        # print("resdatas",resdatas)
                        tree_data = self.usego.build_tree(resdatas)

                        self.usego.sendlog(f'用户菜单结果：{tree_data}')
                        res = ResMsg(data=tree_data)
                        responseData = res.to_json()

                        return responseData

        else:
            self.usego.sendlog(f'非法查询：{sql_data}')
            res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
            responseData = res.to_json()

            return responseData

