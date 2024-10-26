# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 16:31
@Author ： eblis
@File ：splicing_manage.py
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
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.socialPlatforms.telegraGO.telegraSelenium import telegraSelenium
from backendServices.src.assistance.spliceGo import spliceGo
from backendServices.src.awsMQ.amazonSQS import amazonSQS


class splicingManage():
    def __init__(self):
        self.bp = Blueprint("splicing", __name__, url_prefix="/splicing")
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.tele = telegraSelenium()
        self.aws_sqs = amazonSQS()
        
        self.bp.route(self.Myenum.SPLICING_SUBMIT_PUSH, methods=['POST'])(self.splicing_submit_push)
        self.bp.route(self.Myenum.SPLICING_INSERT, methods=['POST'])(self.splicing_insert)
        self.bp.route(self.Myenum.SPLICING_LIST, methods=['GET'])(self.splicing_list)


    def splicing_list(self):
        """
            @Datetime ： 2024/10/21 00:28
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post", limit=10000)
        resdatas = []
        # print("sql_data", sql_data)
        if "sql 语句异常" not in str(sql_data):
            try:
                if len(sql_data) > 0:
                    for i in range(len(sql_data)):
                        thisdata = {
                            "id": i,
                            "url": sql_data[i]["url"],
                            "platform": sql_data[i]["platform"],
                            "genre": sql_data[i]["genre"],
                            "created_at": self.usego.turn_isoformat(sql_data[i]["created_at"])
                        }
                        resdatas.append(thisdata)

                    self.usego.sendlog(f'list结果：{resdatas}')
                    res = ResMsg(data=resdatas)
                    responseData = res.to_json()
                else:
                    self.usego.sendlog(f'list结果：{resdatas}')
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

    def splicing_insert(self):

        data_request = request.json
        zyurl = data_request['zyurl']
        url = data_request['url']
        genre = data_request['genre']
        platform = data_request['platform']

        zyurl_list = zyurl.split(",")
        url_list = url.split(",")
        spl = spliceGo()
        result = spl.splice_301(zyurl_list, url_list, platform, genre)
        if result is not None:
            self.usego.sendlog(f'添加成功：{result}')
            res = ResMsg(data=result)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'入库失败')
            res = ResMsg(code='B0001', msg=f'v')
            responseData = res.to_json()

        return responseData


        
    def splicing_submit_push(self):
        data_request = request.json
        alt_text = data_request['alt_text']
        stacking_min = data_request['stacking_min']
        stacking_max = data_request['stacking_max']
        genre = data_request['genre']
        platform = data_request['platform']
        sql_data = self.ssql.pcSettings_select_sql(platform=platform, state=0)
        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0],
                             'group': item[1],
                             'name': item[2],
                             'address': item[3],
                             'account': item[4],
                             'password': item[5],
                             'platform': item[6],
                             'state': item[7],
                              'remark': item[8],
                             'create_at': self.usego.turn_isoformat(item[9]),
                             'update_at': self.usego.turn_isoformat(item[10])
                             } for item in sql_data]

            except Exception as e:
                self.usego.sendlog(f'没有可用的客户端：{e}')
                res = ResMsg(code='B0001', msg=f'没有可用的客户端')
                return res.to_json()
            else:
                self.usego.sendlog(f'有 {len(resdatas)} 设备符合')
                if resdatas != []:

                    if platform == "telegra":
                        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post", genre=genre,
                                                                       platform=platform)
                        all_links = [data["url"] for data in sql_data] if sql_data else []
                        self.usego.sendlog(f'有 {len(all_links)} 连接需要发送')
                        # 平分 all_links
                        if len(resdatas) > 1:
                            # 计算每份的大小，使用列表切片将 all_links 平均分割
                            avg_size = len(all_links) // len(resdatas)
                            split_links = [all_links[i:i + avg_size] for i in range(0, len(all_links), avg_size)]

                            # 如果有多余的链接，分配到前几个子列表
                            remainder = len(all_links) % len(resdatas)
                            for i in range(remainder):
                                split_links[i].append(all_links[avg_size * len(resdatas) + i])
                        else:
                            split_links = all_links  # 只有一个 resdatas，则不分割

                        # 给每个客户端分配对应的链接子列表
                        self.usego.sendlog(f'开始干活啦')
                        results = []
                        for idx, client in enumerate(resdatas):
                            queue_response = self.aws_sqs.initialization(f'client_{client["name"]}')
                            queue_url = queue_response['QueueUrl']
                            task_data = {
                                'command': 'run_telegra_selenium',
                                'all_links': split_links if len(resdatas) == 1 else split_links[idx],  # 直接分配链接列表
                                'alt_text': alt_text,
                                'stacking_min': stacking_min,
                                'stacking_max': stacking_max,
                            }

                            try:
                                # 发送任务并接收结果
                                self.aws_sqs.send_task(queue_url, task_data)
                                result = self.aws_sqs.receive_result(queue_url)
                                if result:
                                    results.append(result)
                            finally:
                                # 无论是否成功接收到结果，都删除队列
                                self.aws_sqs.delFIFO(queue_url)

                        # 根据 results 内容返回相应的响应
                        res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
                        return res.to_json()
                    else:
                        self.usego.sendlog(f'收到的指令错误:{platform}')
                        res = ResMsg(code='B0001', msg=f'收到的指令错误')
                        return res.to_json()


                else:
                    self.usego.sendlog(f'没有可用的客户端{resdatas}')
                    res = ResMsg(code='B0001', msg=f'没有可用的客户端')
                    return res.to_json()




        else:
            self.usego.sendlog(f'没有可用的客户端：{sql_data}')
            res = ResMsg(code='B0001', msg=f'没有可用的客户端')

            return res.to_json()


