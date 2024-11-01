# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/27 20:23
@Author ： eblis
@File ：amazon_management.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.public.returnMsg import ResMsg

from flask import Blueprint,request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.awsMQ.amazonSQS import AmazonSQS

class amazonManage():
    def __init__(self):
        self.bp = Blueprint("amazon", __name__, url_prefix="/ama")
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.aws_sqs = AmazonSQS()

        # 将路由和视图函数绑定到蓝图

        self.bp.route(self.Myenum.AMAZONSQS_LIST, methods=['GET'])(self.amazonSQS_list)
        self.bp.route(self.Myenum.AMAZONSQS_DELETE, methods=['POST'])(self.amazonSQS_delete)



    def amazonSQS_list(self):

        response = self.aws_sqs.list_queues()
        queues = response.get('QueueUrls', [])
        self.usego.sendlog(f'queues：{queues}')
        resdatas = []

        if queues:
            for i in range(len(queues)):
                queues_data = {
                    "id": "",
                    "url": ""
                }
                queues_data["id"] = i
                queues_data["url"] = queues[i]

                resdatas.append(queues_data)

            self.usego.sendlog(f'list结果：{resdatas}')
            res = ResMsg(data=resdatas)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'list没数据：{queues}')
            res = ResMsg(code='B0001', msg=f'list没数据：{queues}')
            responseData = res.to_json()


        return responseData


    def amazonSQS_delete(self):
        data_request = request.json
        url = data_request['url']
        # print("queue_url",url)

        self.aws_sqs.delFIFO(url)

        self.usego.sendlog(f'成功删除：{url}')
        res = ResMsg(data="成功删除")
        responseData = res.to_json()

        return responseData

