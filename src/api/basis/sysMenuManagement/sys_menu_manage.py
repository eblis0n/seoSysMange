# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/26 23:45
@Author ： eblis
@File ：sys_menu_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
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
import middleware.public.configurationCall as configCall


class menuDeploy():
    def __init__(self):
        self.bp = Blueprint("menuDeploy", __name__, url_prefix="/sys/menu")
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图

        self.bp.route(self.Myenum.SYS_MENU_LIST, methods=['GET'])(self.sys_menu_list)
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
                        self.usego.sendlog(f'最新的请求不到，用默认的')
                        default_tree_data = self.sys_menu_routes_default()
                        res = ResMsg(data=default_tree_data)

                    else:
                        # print("resdatas",resdatas)
                        tree_data = self.usego.build_tree(resdatas)

                        self.usego.sendlog(f'用户菜单结果：{tree_data}')
                        res = ResMsg(data=tree_data)
                    return res.to_json()
                else:
                    self.usego.sendlog(f'最新的请求不到，用默认的')
                    default_tree_data = self.sys_menu_routes_default()
                    res = ResMsg(data=default_tree_data)

            return res.to_json()

        else:
            # self.usego.sendlog(f'非法查询：{sql_data}')
            # res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
            default_tree_data = self.sys_menu_routes_default()
            self.usego.sendlog(f'用户菜单结果：{default_tree_data}')
            res = ResMsg(data=default_tree_data)

            return res.to_json()


    def sys_menu_list(self):
        """
        @Datetime ： 2024/10/23 22:33
        @Author ：eblis
        @Motto：获取菜单列表
        """
        # 从数据库获取菜单数据
        sql_data = self.ssql.menu_list()
        if "sql 语句异常" not in str(sql_data):
            resdatas = [{'id': item[0], 'name': item[1], 'parent_id': item[2], 'route_name': item[3],
        'route_path': item[4], 'component': item[5], 'icon': item[6], 'sort': item[7], 'visible': item[8], 'redirect': item[9], 'type': item[10], 'always_show': item[11], 'keep_alive': item[12], 'params': item[13],"children": [] } for item in sql_data]
            # print("sys_menu_list",resdatas)
            # 构建树形结构
            tree_data = self.usego.build_tree(resdatas)

            self.usego.sendlog(f'菜单列表结果：{tree_data}')
            res = ResMsg(data=tree_data)
        else:
            self.usego.sendlog(f'获取菜单列表失败:{sql_data}')
            res = ResMsg(code='B0001', msg=f'获取菜单列表失败')
        return res.to_json()



    ######################################## 调试 #####################################################################
    #
    def sys_menu_routes_default(self):
        """
            @Datetime ： 2024/9/27 00:00
            @Author ：eblis
            @Motto：管理后台用户管理
        """
        with open(configCall.menu_path, 'r', encoding='utf-8') as f:
            try:
                tree_data = json.load(f)
            except:
                tree_data = []

        return tree_data

