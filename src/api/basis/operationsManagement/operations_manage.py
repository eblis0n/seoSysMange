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
import time

from bson import ObjectId

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
        self.bp.route(self.Myenum.HOSTS_DISABLE, methods=['POST'])(self.hosts_disable)
        self.bp.route(self.Myenum.HOSTS_UPDATE, methods=['POST'])(self.hosts_update)

        self.bp.route(self.Myenum.TASKS_LIST, methods=['GET'])(self.tasks_list)
        self.bp.route(self.Myenum.TASK_IMPLEMENT_LOGS, methods=['POST'])(self.task_implement_logs)
        self.bp.route(self.Myenum.TASKS_INSERT, methods=['POST'])(self.tasks_insert)

    def hosts_list(self):
        """
            @Datetime ： 2024/11/3 15:42
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mossql.operations_hosts_find("seo_operations_hosts")
        resdatas = []
        current_time = datetime.now()

        if not sql_data:  # 如果sql_data为空或None，直接返回
            self.usego.sendlog(f'list查询失败：{sql_data}')
            return ResMsg(code='B0001', msg='list查询失败').to_json()

        for record in sql_data:
            # 提取数据
            thisdata = {
                "id": str(record["_id"]),  # 转换 ObjectId 为字符串
                "host_ip": record["host_ip"],
                "is_disabled": str(record["is_disabled"]),
                "host_group": record["host_group"],
                "remark": record["remark"],
                "ping_time": record["ping_time"],
                "online": "1"  # 默认离线
            }

            # 获取ping时间并判断是否在线
            ping_time = self.parse_ping_time(thisdata["ping_time"])
            if ping_time:
                # 如果ping时间在5分钟内，视为在线
                minutes_ago = current_time - timedelta(seconds=int(configCall.refreshTiming))
                if ping_time > minutes_ago:
                    thisdata["online"] = "0"  # 视为在线

            resdatas.append(thisdata)

        self.usego.sendlog(f'list结果：{len(resdatas)}')
        return ResMsg(data=resdatas).to_json()




    def hosts_disable(self):
        """
            @Datetime ： 2024/11/3 15:42
            @Author ：eblis
            @Motto：status=0 为有效，status=1 为 无效
        """

        data_request = request.json

        # 定义查询条件
        query = {
            "_id": ObjectId(f"{data_request['id']}")
        }

        # 定义更新内容
        update = {
            "is_disabled": int(data_request['is_disabled']),

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
            "_id": ObjectId(f"{data_request['id']}")
        }

        # 定义更新内容
        update = {
            "is_disabled": int(data_request['is_disabled']),
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

    ##################################################### tasks ###########################################################

    def tasks_insert(self):
        """
            @Datetime ： 2024/11/8 14:18
            @Author ：eblis
            @Motto：简单描述用途
        """
        data_request = request.json
        # content = data_request["script_content"]
        # if isinstance(content, dict):
        #     content = json.dumps(content)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = {
            "task_id": self.generate_task_id(),
            "host_ip": data_request["host_ip"],
            "script_name": data_request["script_name"],
            "script_content": str(data_request["script_content"]),
            "task_type": data_request["task_type"],
            "status": "Pending",
            "result": "",
            "created_at": created_at,
            "completed_at": "",
            "last_update": ""
        }
        sql_data = self.mossql.operations_tasks_insert("seo_operations_tasks", query)


        if sql_data is not None:
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data="成功")


        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()


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


        query = {"task_id": data_request['task_id']}


        sql_data = self.mossql.operations_tasks_logs_find("seo_operations_logs", query)
        resdatas = []
        # print("sql_data", sql_data)
        if sql_data is not None:
            try:
                if len(sql_data) > 0:
                    for i in range(len(sql_data)):
                        thisdata = {
                            "id": str(sql_data[i]["_id"]),
                            "task_id": sql_data[i]["task_id"],
                            "task_type": sql_data[i]["task_type"],
                            "log_content": sql_data[i]["log_content"],
                            "log_time": self.usego.turn_isoformat(sql_data[i]["log_time"]),
                            "status": sql_data[i]["status"]
                        }
                        resdatas.append(thisdata)

                    self.usego.sendlog(f'logs结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
                else:
                    self.usego.sendlog(f'logs结果：{len(resdatas)}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
            except Exception as e:
                self.usego.sendlog(f'logs查询失败：{e}')
                res = ResMsg(code='B0001', msg=f'logs查询失败')
                responseData = res.to_json()
        else:
            self.usego.sendlog(f'logs查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'logs查询失败')
            responseData = res.to_json()

        return responseData

################################################################# 非接口 #########################################

    def generate_task_id(self):
        """生成基于时间戳的任务ID"""
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳
        random_suffix = self.usego.randomRandint(100, 999)  # 3位随机数
        return f"{timestamp}{random_suffix}"

    def parse_ping_time(self, ping_time_str):
        """
        封装时间解析功能，确保代码结构清晰。
        """
        try:
            # 根据实际时间格式调整解析
            return datetime.strptime(ping_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.usego.sendlog(f'无效的时间格式: {ping_time_str}')
            return None



################################################################# 调试 #########################################


    # def hosts_list(self):
    #     """
    #         @Datetime ： 2024/11/3 15:42
    #         @Author ：eblis
    #         @Motto：简单描述用途
    #     """
    #
    #     resdatas = [
    #         {
    #             "id": "671b2ed492d279da1e511080",
    #             "host_ip": "140.240.16.154",
    #             "is_disabled": "1",
    #             "host_group": "hugo",
    #             "remark": "测试",
    #             "ping_time": "2024-10-27 15:16:06",
    #             "online": "1"
    #         },
    #         {
    #             "id": "671cfa6292d279da1e511081",
    #             "host_ip": "8.217.41.149",
    #             "is_disabled": "0",
    #             "host_group": "hugo",
    #             "remark": "测试",
    #             "ping_time": "2024-11-06 17:09:06",
    #             "online": "0"
    #         }
    #     ]
    #
    #     self.usego.sendlog(f'list结果：{len(resdatas)}')
    #     return ResMsg(data=resdatas).to_json()