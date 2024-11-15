# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/8/21 19:48
@Author ： eblis
@File ：note_info_manegement.py
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
from middleware.control.taskAws import taskAws

class noteInfoManage():
    def __init__(self):
        self.bp = Blueprint("noteInfo", __name__, url_prefix="/note")
        self.Myenum = MyEnum()

        self.ssql = basis_sqlGO()
        self.usego = otherUse()
        self.task = taskAws()




        self.bp.route(self.Myenum.NOTE_INFO_LIST, methods=['GET'])(self.note_info_list)
        self.bp.route(self.Myenum.NOTE_INFO_INSERT, methods=['POST'])(self.note_info_insert)
        self.bp.route(self.Myenum.NOTE_INFO_UPDATE, methods=['POST'])(self.note_info_update)
        self.bp.route(self.Myenum.NOTE_INFO_DELETE, methods=['POST'])(self.note_info_del)
        # self.bp.route(self.Myenum.NOTE_USER_POST, methods=['POST'])(self.note_user_post)
        # self.bp.route(self.Myenum.NOTE_BATCH_PUSH_ARTICLE, methods=['POST'])(self.NOTE_USER_BATCH_PUSH_ARTICLE)
        self.bp.route(self.Myenum.NOTE_BATCH_GET_COOKIE, methods=['POST'])(self.note_batch_get_cookie)
        # self.bp.route(self.Myenum.NOTE_USER_GET_COOKIE, methods=['POST'])(self.note_user_get_cookie)

    def note_info_list(self):
        sql_data = self.ssql.note_users_info_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [
                    {'id': item[0], 'group': item[1], 'adsNumber': item[2], 'adsID': item[3], 'username': item[4],
                     'email': item[5], 'password': item[6], 'proxies': item[7],
                     'cookie': item[8], 'create_at': self.usego.turn_isoformat(item[9]), 'update_at': self.usego.turn_isoformat(item[10])} for item in sql_data]


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




    def note_info_insert(self):
        """
            @Datetime ： 2024/7/30 17:06
            @Author ：eblis
            @Motto：简单描述用途
        """

        form_data = request.json
        group = form_data['group']
        adsNumber = form_data['adsNumber']
        adsID = form_data['adsID']
        username = form_data['username']
        email = form_data['email']
        proxies = form_data['proxies']
        password = form_data['password']
        cookie = form_data['cookie']
        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql_data = self.ssql.note_users_info_insert(group, adsNumber, adsID, username, email, password, proxies, cookie, create_at)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()



    def note_info_del(self):
        """
            @Datetime ： 2024/7/30 17:06
            @Author ：eblis
            @Motto：简单描述用途
        """

        form_data = request.json
        id = form_data['id']


        sql_data = self.ssql.note_user_info_del(id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def note_info_update(self):
        """
            @Datetime ： 2024/8/22 21:52
            @Author ：eblis
            @Motto：简单描述用途
        """
        form_data = request.json
        id = form_data['id']
        adsID = form_data['adsID']
        type = form_data['type']
        if type == "basis":
            group = form_data['group']

            adsNumber = form_data['adsNumber']
            username = form_data['username']
            email = form_data['email']
            password = form_data['password']
            proxies = form_data['proxies']
            cookie = form_data['cookie']

            sql_data = self.ssql.note_users_info_update(group, adsNumber, adsID, username, email, password, proxies, cookie, id)
            if "sql 语句异常" not in str(sql_data):
                self.usego.sendlog(f'更新成功：{sql_data}')
                res = ResMsg(data=sql_data)

            else:
                self.usego.sendlog(f'更新失败：{sql_data}')
                res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')
            return res.to_json()
        else:
            datasDict = {
                "platform": "blogger",
                "adsIDlist": [adsID]
            }
            self.usego.sendlog(f"接收到的参数：{datasDict}")
            results = self.task.run("cookies", datasDict["platform"], datasDict)

            res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
            return res.to_json()






    #
    # def note_user_post(self):
    #
    #     form_data = request.json
    #     username = form_data['username']
    #     cookie = form_data['cookie']
    #     proxies = form_data['proxies']
    #
    #     tasks_args = []
    #     tasks_args.append((self.notesP.run, (username, cookie, proxies)))
    #
    #
    #     self.mul.pro_task_go(self.mul.note_post_pool_go, (1, tasks_args))
    #
    #     self.usego.sendlog(f'正在触发 note 脚本发帖')
    #     res = ResMsg(data=f'正在触发 note 脚本发帖')
    #     responseData = res.to_dict()
    #     return responseData
    #
    #
    # def note_user_batch_post(self):
    #
    #     form_data = request.json
    #     group = form_data['group']
    #
    #     if group == "None":
    #         print("把所有用户都发一篇文章")
    #         sql_data = self.ssql.note_users_info_list_sql()
    #
    #         if "sql 语句异常" not in str(sql_data):
    #             resdatas = [
    #                 {'id': item[0], 'group': item[1], 'adsid': item[2], 'adsuser': item[3], 'username': item[4],
    #                  'email': item[5], 'password': item[6], 'proxies': item[7],
    #                  'cookie': item[8], 'create_at': self.usego.turn_isoformat(item[9])} for item in sql_data]
    #         else:
    #             self.usego.sendlog(f'{sql_data}查数据库失败')
    #             res = ResMsg(code=10001, msg=f'{sql_data}查数据库失败')
    #             responseData = res.to_json()
    #             return responseData
    #     else:
    #         sql_data = self.ssql.note_users_info_select_sql(group)
    #
    #         if "sql 语句异常" not in str(sql_data):
    #             resdatas = [
    #                 {'id': item[0], 'group': item[1], 'adsid': item[2], 'adsuser': item[3], 'username': item[4],
    #                  'email': item[5], 'password': item[6], 'proxies': item[7],
    #                  'cookie': item[8], 'create_at': self.usego.turn_isoformat(item[9])} for item in sql_data]
    #         else:
    #             self.usego.sendlog(f'{sql_data}查数据库失败')
    #             res = ResMsg(code=10001, msg=f'{sql_data}查数据库失败')
    #             responseData = res.to_json()
    #             return responseData
    #
    #
    #     tasks_args = []
    #     for resdata in resdatas:
    #         tasks_args.append((self.notesP.run, (resdata['username'], resdata['cookie'], resdata['proxies'])))
    #
    #
    #     self.mul.pro_task_go(self.mul.note_post_pool_go, (1, tasks_args))
    #
    #     self.usego.sendlog(f'{group}正在触发 note 脚本发帖')
    #     res = ResMsg(data=f'{group}正在触发 note 脚本发帖')
    #     responseData = res.to_dict()
    #     return responseData
    #
    #
    #
    # def note_user_get_cookie(self):
    #
    #     form_data = request.json
    #     adsuser = form_data['adsuser']
    #
    #     resdatas = []
    #     resdatas.append(adsuser)
    #
    #     tasks_args = []
    #     # print("resdatas", resdatas)
    #
    #     tasks_args.append((self.getGO.run, (resdatas, )))
    #
    #
    #     self.mul.pro_task_go(self.mul.note_get_cookie_pool_go, (1, tasks_args))
    #
    #     self.usego.sendlog(f'{adsuser}正在触发 更新cookie 脚本发帖')
    #     res = ResMsg(data=f'{adsuser}正在触发 更新cookie 脚本发帖')
    #     responseData = res.to_dict()
    #     return responseData
    #
    def note_batch_get_cookie(self):

        form_data = request.json
        group = form_data['group']

        if group == "All" or group == "":
            print("把所有用户都重新获取cookie")
            sql_data = self.ssql.note_users_info_list_sql()

            if "sql 语句异常" not in str(sql_data):
                resdatas = [item[3] for item in sql_data]

            else:
                self.usego.sendlog(f'{sql_data}查数据库失败')
                res = ResMsg(code='B0001', msg=f'{sql_data}查数据库失败')
                return res.to_json()
        else:
            sql_data = self.ssql.note_users_info_select_sql(group)

            if "sql 语句异常" not in str(sql_data):
                resdatas = [item[3] for item in sql_data]
            else:
                self.usego.sendlog(f'{sql_data}查数据库失败')
                res = ResMsg(code='B0001', msg=f'{sql_data}查数据库失败')
                return res.to_json()

        datasDict = {
            "platform": "blogger",
            "adsIDlist": resdatas
        }
        self.usego.sendlog(f"接收到的参数：{datasDict}")
        results = self.task.run("cookies", datasDict["platform"], datasDict)

        res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        return res.to_json()



