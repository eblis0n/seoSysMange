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

from flask import Blueprint
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



    def amazonSQS_list(self):

        response = self.aws_sqs.list_queues()
        queues = response.get('QueueUrls', [])
        resdatas = []
        if queues:
            data = {
                "id":"",
                "url":""

            }
            for idx, queue in queues:
                data["id"] = idx
                data["url"] = queue


            self.usego.sendlog(f'list结果：{resdatas}')
            res = ResMsg(data=resdatas)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'list没数据：{queues}')
            res = ResMsg(code='B0001', msg=f'list没数据：{queues}')
            responseData = res.to_json()


        return responseData

