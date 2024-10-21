# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/29 13:35
@Author ： eblis
@File ：urlSet.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

class MyEnum():

    # 上传文件
    UPLOAD_FILE = "/file/"


    # 系统用户管理
    SYS_USER_LOGIN = "/login/"
    SYS_USER_LOGOUT = "/logout/"
    SYS_USER_LIST = "/list/"
    SYS_USER_INFO = "/info/"


    # 菜单
    SYS_MENU_ROUTES = "/routes/"



    # pc
    PC_INSERT = "/insert/"
    PC_DELETE = "/delete/"
    PC_UPDATE = "/update/"
    PC_LIST = "/list/"


    #telegra
    SUBMIT_301 = "/301/"
    SPLICING_LIST = "/list/"