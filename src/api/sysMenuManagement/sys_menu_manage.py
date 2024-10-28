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

        self.bp.route(self.Myenum.SYS_MENU_LIST, methods=['GET'])(self.sys_menu_list)
        self.bp.route(self.Myenum.SYS_MENU_ROUTES, methods=['GET'])(self.sys_menu_routes)

    # def sys_menu_routes(self):
    #     """
    #         @Datetime ： 2024/9/27 00:00
    #         @Author ：eblis
    #         @Motto：管理后台用户管理
    #     """
    #     user_id = get_verify_token()
    #     # print("user_id",user_id)
    #     sql_data = self.ssql.sys_user_router_code_select(user_id)
    #     # print("sql_data",sql_data)
    #
    #     if "sql 语句异常" not in str(sql_data):
    #         try:
    #             router_code = [item[0] for item in sql_data]
    #
    #         except:
    #             self.usego.sendlog(f'查无此数据：{sql_data}')
    #             res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
    #             responseData = res.to_json()
    #
    #             return responseData
    #         else:
    #             self.usego.sendlog(f'router_code：{router_code}')
    #             time.sleep(5)
    #             sql_data = self.ssql.menu_router_list(router_code, 4)
    #             # print("sql_data",sql_data)
    #             if "sql 语句异常" not in str(sql_data):
    #                 try:
    #                     resdatas = [{'id': item[0], 'name': item[1], 'parent_id': item[2], 'route_name': item[3],
    #                                  'route_path': item[4], 'component': item[5], 'icon': item[6], 'sort': item[7], 'visible': item[8], 'redirect': item[9], 'type': item[10], 'always_show': item[11], 'keep_alive': item[12], 'params': item[13]} for item in sql_data]
    #
    #                 except:
    #                     self.usego.sendlog(f'菜单查询失败：{sql_data}')
    #                     res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
    #                     responseData = res.to_json()
    #
    #                     return responseData
    #                 else:
    #                     # print("resdatas",resdatas)
    #                     tree_data = self.usego.build_tree(resdatas)
    #
    #                     self.usego.sendlog(f'用户菜单结果：{tree_data}')
    #                     res = ResMsg(data=tree_data)
    #                     responseData = res.to_json()
    #
    #                     return responseData
    #
    #     else:
    #         self.usego.sendlog(f'非法查询：{sql_data}')
    #         res = ResMsg(code='B0001', msg=f'查无此用户，请查正后再重试')
    #         responseData = res.to_json()
    #
    #         return responseData


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

            # 构建树形结构
            tree_data = self.usego.build_tree(resdatas)

            self.usego.sendlog(f'菜单列表结果：{tree_data}')
            res = ResMsg(data=tree_data)
        else:
            self.usego.sendlog(f'获取菜单列表失败:{sql_data}')
            res = ResMsg(code='B0001', msg=f'获取菜单列表失败')
        return res.to_json()



    ######################################## 调试 #####################################################################

    def sys_menu_routes(self):
        """
            @Datetime ： 2024/9/27 00:00
            @Author ：eblis
            @Motto：管理后台用户管理
        """
        tree_data = [
        {
            "path": "/outcome",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u7ed3\u679c\u5c55\u793a",
                "icon": "cascader",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "telegra",
                    "component": "outcome/teleUpshot/index",
                    "redirect": "",
                    "name": "outcome",
                    "meta": {
                        "title": "telegra\u7ed3\u679c",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        },
        {
            "path": "/implement",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u6267\u884c\u7ba1\u7406",
                "icon": "cascader",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "queue",
                    "component": "implement/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u961f\u5217\u7ba1\u7406",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": False,
                        "alwaysShow": True,
                        "params": ""
                    },
                    "children": [
                        {
                            "path": "amazonsqs",
                            "component": "implement/amazonsqs/index",
                            "redirect": "",
                            "name": "amazonsqs",
                            "meta": {
                                "title": "AmazonSQS",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": True,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        }
                    ]
                },
                {
                    "path": "mission",
                    "component": "implement/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u4efb\u52a1\u7ba1\u7406",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": False,
                        "alwaysShow": True,
                        "params": ""
                    },
                    "children": [
                        {
                            "path": "Splicing",
                            "component": "implement/Splicing/index",
                            "redirect": "",
                            "name": "go301",
                            "meta": {
                                "title": "\u62fc\u63a5",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": True,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        }
                    ]
                }
            ]
        },
        {
            "path": "/basis",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u4fe1\u606f\u5e93",
                "icon": "cascader",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "platform",
                    "component": "basisManage/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u5e73\u53f0\u4fe1\u606f",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": False,
                        "alwaysShow": True,
                        "params": ""
                    },
                    "children": [
                        {
                            "path": "ads",
                            "component": "basisManage/AdsBasic/adsBasic",
                            "redirect": "",
                            "name": "ads",
                            "meta": {
                                "title": "ads\u76f8\u5173",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": False,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        },
                        {
                            "path": "blogger",
                            "component": "basisManage/Blogger/blogger",
                            "redirect": "",
                            "name": "Blogger",
                            "meta": {
                                "title": "Blogger",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": False,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        },
                        {
                            "path": "note",
                            "component": "basisManage/NoteUserInfo/noteUserInfo",
                            "redirect": "",
                            "name": "Note",
                            "meta": {
                                "title": "Note",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": False,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        },
                        {
                            "path": "youtube",
                            "component": "basisManage/YouTube/YouTubeChannelSubtitle",
                            "redirect": "",
                            "name": "YouTube",
                            "meta": {
                                "title": "YouTube",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": False,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        },
                        {
                            "path": "googleOauth",
                            "component": "basisManage/GoogleOauth/googleOauth",
                            "redirect": "",
                            "name": "googleOauth",
                            "meta": {
                                "title": "googleOauth",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": False,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        }
                    ]
                },
                {
                    "path": "other",
                    "component": "basisManage/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u5176\u4ed6\u4fe1\u606f",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": False,
                        "alwaysShow": True,
                        "params": ""
                    },
                    "children": [
                        {
                            "path": "PCclient",
                            "component": "basisManage/PCclient/index",
                            "redirect": "",
                            "name": "PCclient",
                            "meta": {
                                "title": "pc\u7ba1\u7406",
                                "icon": "",
                                "hidden": False,
                                "keepAlive": True,
                                "alwaysShow": False,
                                "params": ""
                            },
                            "children": [

                            ]
                        }
                    ]
                }
            ]
        },
        {
            "path": "/articleManage",
            "component": "Layout",
            "redirect": "https://juejin.cn/post/7228990409909108793",
            "name": "",
            "meta": {
                "title": "\u6587\u7ae0\u5e93",
                "icon": "document",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "AiPrompt",
                    "component": "articleManage/AItrain/aiTrain",
                    "redirect": "",
                    "name": "aiTrain",
                    "meta": {
                        "title": "AiPrompt",
                        "icon": "el-icon-Star",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "articleSort",
                    "component": "articleManage/sort/index",
                    "redirect": "",
                    "name": "sort",
                    "meta": {
                        "title": "\u884c\u4e1a\u5206\u7c7b",
                        "icon": "el-icon-StarFilled",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "article",
                    "component": "articleManage/article/aiArticle",
                    "redirect": "",
                    "name": "article",
                    "meta": {
                        "title": "\u6587\u7ae0",
                        "icon": "el-icon-StarFilled",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        },
        {
            "path": "/codegen",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u7cfb\u7edf\u5de5\u5177",
                "icon": "menu",
                "hidden": False,
                "keepAlive": True,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "codegen",
                    "component": "codegen/index",
                    "redirect": "",
                    "name": "Codegen",
                    "meta": {
                        "title": "\u4ee3\u7801\u751f\u6210",
                        "icon": "code",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        },
        {
            "path": "/reports",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u62a5\u8868\u5e93",
                "icon": "api",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": True,
                "params": ""
            },
            "children": [
                {
                    "path": "googleRecord",
                    "component": "reportsManage/googleRecord/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": " Google\u6536\u5f55",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "spider",
                    "component": "reportsManage/spider/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u8718\u86db",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        },
        {
            "path": "/api",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u63a5\u53e3\u6587\u6863",
                "icon": "api",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": True,
                "params": ""
            },
            "children": [
                {
                    "path": "https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/164286",
                    "component": "",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "apidocs",
                        "icon": "link",
                        "hidden": False,
                        "keepAlive": False,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/164286",
                    "component": "",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "yescaptcha",
                        "icon": "link",
                        "hidden": False,
                        "keepAlive": False,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        },
        {
            "path": "/system",
            "component": "Layout",
            "redirect": "/system/user",
            "name": "",
            "meta": {
                "title": "\u7cfb\u7edf\u7ba1\u7406",
                "icon": "system",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "user",
                    "component": "system/user/index",
                    "redirect": "",
                    "name": "User",
                    "meta": {
                        "title": "\u7528\u6237\u7ba1\u7406",
                        "icon": "el-icon-User",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "role",
                    "component": "system/role/index",
                    "redirect": "",
                    "name": "Role",
                    "meta": {
                        "title": "\u89d2\u8272\u7ba1\u7406",
                        "icon": "role",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "menu",
                    "component": "system/menu/index",
                    "redirect": "",
                    "name": "Menu",
                    "meta": {
                        "title": "\u83dc\u5355\u7ba1\u7406",
                        "icon": "menu",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "dept",
                    "component": "system/dept/index",
                    "redirect": "",
                    "name": "Dept",
                    "meta": {
                        "title": "\u90e8\u95e8\u7ba1\u7406",
                        "icon": "tree",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "dict",
                    "component": "system/dict/index",
                    "redirect": "",
                    "name": "Dict",
                    "meta": {
                        "title": "\u5b57\u5178\u7ba1\u7406",
                        "icon": "dict",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "log",
                    "component": "system/log/index",
                    "redirect": "",
                    "name": "Log",
                    "meta": {
                        "title": "\u7cfb\u7edf\u65e5\u5fd7",
                        "icon": "document",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        },
        {
            "path": "/component",
            "component": "Layout",
            "redirect": "",
            "name": "",
            "meta": {
                "title": "\u7ec4\u4ef6\u5c01\u88c5",
                "icon": "menu",
                "hidden": False,
                "keepAlive": False,
                "alwaysShow": False,
                "params": ""
            },
            "children": [
                {
                    "path": "curd",
                    "component": "demo/curd/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u589e\u5220\u6539\u67e5",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "table-select",
                    "component": "demo/table-select/index",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u5217\u8868\u9009\u62e9\u5668",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "wang-editor",
                    "component": "demo/wang-editor",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u5bcc\u6587\u672c\u7f16\u8f91\u5668",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "upload",
                    "component": "demo/upload",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u56fe\u7247\u4e0a\u4f20",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "dict-demo",
                    "component": "demo/dict",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u5b57\u5178\u7ec4\u4ef6",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                },
                {
                    "path": "icon-selector",
                    "component": "demo/icon-selector",
                    "redirect": "",
                    "name": "",
                    "meta": {
                        "title": "\u56fe\u6807\u9009\u62e9\u5668",
                        "icon": "",
                        "hidden": False,
                        "keepAlive": True,
                        "alwaysShow": False,
                        "params": ""
                    },
                    "children": [

                    ]
                }
            ]
        }
    ]
        res = ResMsg(data=tree_data)
        responseData = res.to_json()

        return responseData

