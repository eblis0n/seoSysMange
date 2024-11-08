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
    SYS_MENU_LIST = "/list/"
    # SYS_MENU_OPTIONS = "/options/"
    # SYS_MENU_FORM = "/form/"
    # SYS_MENU_ADD = "/add/"
    # SYS_MENU_UPDATE = "/update/"
    # SYS_MENU_DELETE = "/del/"



    # pc
    PC_INSERT = "/insert/"
    PC_DELETE = "/delete/"
    PC_UPDATE = "/update/"
    PC_LIST = "/list/"


    #splicing
    SPLICING_SUBMIT_PUSH = "/push/"
    SPLICING_LIST = "/list/"
    SPLICING_INSERT = "/add/"
    SPLICING_TOTAL = "/total/"
    SPLICING_DELETE_ALL = "/delete/"

    # public
    PLATFORMS = "/platforms/"

    # amazon
    AMAZONSQS_LIST = "/list/"
    AMAZONSQS_DELETE = "/delete/"



    # outcome
    OUTCOME_LIST = "/list/"
    OUTCOME_TOTAL = "/total/"
    OUTCOME_DELETE_DATA = "/delete/"


    # blogger
    BLOGGER_INFO_LIST = "/list/"
    BLOGGER_INFO_INSERT = "/add/"
    BLOGGER_INFO_UPDATE = "/update/"
    BLOGGER_INFO_DELETE = "/delete/"



    # operations
    HOSTS_LIST = "/hosts/list/"
    HOSTS_UPDATE = "/hosts/update/"
    HOSTS_DISABLE = "/hosts/disable/"
    TASKS_LIST = "/tasks/list/"
    TASKS_INSERT = "/tasks/insert/"
    TASK_IMPLEMENT_LOGS = "/task/logs/"

