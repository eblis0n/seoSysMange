# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/3 15:12
@Author ： eblis
@File ：operations_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys


base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from datetime import datetime, timedelta
from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse
from middleware.public.returnMsg import ResMsg
import middleware.public.configurationCall as configCall



class operationsManage():
    def __init__(self):
        self.bp = Blueprint("operations", __name__, url_prefix="/operations")
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.mossql = mongo_sqlGO()




        self.bp.route(self.Myenum.HOSTS_LIST, methods=['GET'])(self.hosts_list)
        self.bp.route(self.Myenum.TASKS_LIST, methods=['GET'])(self.tasks_list)
        self.bp.route(self.Myenum.HOSTS_UPDATE_STATUS, methods=['POST'])(self.hosts_update_status)
        self.bp.route(self.Myenum.HOSTS_UPDATE, methods=['POST'])(self.hosts_update)
        self.bp.route(self.Myenum.TASK_IMPLEMENT_LOGS, methods=['POST'])(self.task_implement_logs)


        
    def hosts_list(self):
        """
            @Datetime ： 2024/11/3 15:42
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mossql.operations_hosts_find("seo_operations_hosts")
        resdatas = []
        # print("sql_data", sql_data)
        current_time = datetime.now()
        if sql_data is not None:
            try:
                if len(sql_data) > 0:
                    for i in range(len(sql_data)):

                        # 5分钟的时间间隔

                        thisdata = {
                            "id": sql_data[i]["id"],
                            "host_ip": sql_data[i]["host_ip"],
                            "status": sql_data[i]["status"],
                            "host_group": sql_data[i]["host_group"],
                            "remark": sql_data[i]["remark"],
                            "ping_time": sql_data[i]["ping_time"],
                            "online": 0
                        }
                        minutes_ago = current_time - timedelta(seconds=configCall.refreshTiming)
                        if sql_data[i]["ping_time"] > minutes_ago:
                            thisdata["online"] = 1

                        resdatas.append(thisdata)

                    self.usego.sendlog(f'list结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)

                else:
                    self.usego.sendlog(f'list结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)

            except Exception as e:
                self.usego.sendlog(f'list查询失败：{e}')
                res = ResMsg(code='B0001', msg=f'list查询失败')

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败')


        return res.to_json()




    def hosts_update_status(self):
        """
            @Datetime ： 2024/11/3 15:42
            @Author ：eblis
            @Motto：status=0 为有效，status=1 为 无效
        """

        data_request = request.json

        # 定义查询条件
        query = {
            "id": data_request['id']
        }

        # 定义更新内容
        update = {
            "status": data_request['status'],

        }

        sql_data = self.mossql.operations_hosts_update("seo_operations_hosts", query, update)

        if sql_data is not None:
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)
            responseData = res.to_json()

        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')
            responseData = res.to_json()
        return responseData



    def hosts_update(self):
        data_request = request.json

        # 定义查询条件
        query = {
            "id": data_request['id']
        }

        # 定义更新内容
        update = {
            "host_group": data_request['host_group'],
            "remark": data_request['remark']
        }

        sql_data = self.mossql.operations_hosts_update("seo_operations_hosts", query, update)

        if sql_data is not None:
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)


        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')

        return res.to_json()

    ################################################################################################################

    def tasks_list(self):
        """
            @Datetime ： 2024/11/3 16:30
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mossql.operations_tasks_find("seo_operations_tasks")
        resdatas = []
        # print("sql_data", sql_data)
        if sql_data is not None:
            try:
                if len(sql_data) > 0:
                    for i in range(len(sql_data)):
                        thisdata = {
                            "task_id": sql_data[i]["task_id"],
                            "host_ip": sql_data[i]["host_ip"],
                            "script_name": sql_data[i]["script_name"],
                            "script_content": sql_data[i]["script_content"],
                            "status": sql_data[i]["status"],
                            "task_type": sql_data[i]["task_type"],
                            "result": sql_data[i]["result"],
                            "created_at": self.usego.turn_isoformat(sql_data[i]["created_at"]),
                            "completed_at": self.usego.turn_isoformat(sql_data[i]["completed_at"]),
                            "last_update": self.usego.turn_isoformat(sql_data[i]["last_update"])
                        }
                        resdatas.append(thisdata)

                    self.usego.sendlog(f'list结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)

                else:
                    self.usego.sendlog(f'list结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)

            except Exception as e:
                self.usego.sendlog(f'list查询失败：{e}')
                res = ResMsg(code='B0001', msg=f'list查询失败')

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败')

        return res.to_json()

    def task_implement_logs(self):

        data_request = request.json

        task_id = data_request['task_id']
        query = {"task_id": task_id}


        sql_data = self.mossql.operations_tasks_logs_find("seo_operations_logs", query)
        resdatas = []
        # print("sql_data", sql_data)
        if sql_data is not None:
            try:
                if len(sql_data) > 0:
                    for i in range(len(sql_data)):
                        thisdata = {
                            "log_id": sql_data[i]["log_id"],
                            "task_id": sql_data[i]["host_id"],
                            "log_content": sql_data[i]["log_content"],
                            "log_time": sql_data[i]["log_time"],
                            "script_content": sql_data[i]["script_content"],
                            "status": sql_data[i]["status"]
                        }
                        resdatas.append(thisdata)

                    self.usego.sendlog(f'list结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
                else:
                    self.usego.sendlog(f'list结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
            except Exception as e:
                self.usego.sendlog(f'list查询失败：{e}')
                res = ResMsg(code='B0001', msg=f'list查询失败')
                responseData = res.to_json()
        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败')
            responseData = res.to_json()

        return responseData


