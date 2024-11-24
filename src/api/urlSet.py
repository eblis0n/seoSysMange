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
    GOOGLEEXCEL = "/excle/"

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

    # note
    NOTE_INFO_LIST = "/list/"
    NOTE_INFO_INSERT = "/add/"
    NOTE_INFO_UPDATE = "/update/"
    NOTE_INFO_DELETE = "/delete/"
    NOTE_BATCH_GET_COOKIE = "/batch/cookie/"
    NOTE_BATCH_PUSH_ARTICLE = "/batch/article/"



    # operations
    HOSTS_LIST = "/hosts/list/"
    HOSTS_UPDATE = "/hosts/update/"
    HOSTS_DISABLE = "/hosts/disable/"
    TASKS_LIST = "/tasks/list/"
    TASKS_INSERT = "/tasks/insert/"
    TASK_IMPLEMENT_LOGS = "/task/logs/"


    # scriptTemplate
    SCRIPT_TEMPLATE_INSERT = "/add/"
    SCRIPT_TEMPLATE_DELETE = "/delete/"
    SCRIPT_TEMPLATE_LIST = "/list/"
    SCRIPT_TEMPLATE_UPDATE = "/update/"


####################################### 文章库 #########################################################################
    # aiprompt
    AI_PROMPT_LIST = "/list/"
    AI_PROMPT_INSERT = "/add/"
    AI_PROMPT_UPDATE = "/update/"
    AI_PROMPT_DELETE = "/delete/"

    # article
    ARTICLE_LIST = "/list/"
    ARTICLE_INSERT = "/add/"
    ARTICLE_DELETE = "/delete/"

    # category
    CATEGORY_LIST = "/list/"
    CATEGORY_INSERT = "/add/"
    CATEGORY_UPDATE = "/update/"
    CATEGORY_DELETE = "/delete/"




