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
from flask import Blueprint, request
from middleware.public.returnMsg import ResMsg
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
        """列出所有 SQS 队列"""
        response = self.aws_sqs.list_queues()
        queues = response.get('QueueUrls', [])
        self.usego.sendlog(f'queues：{queues}')
        resdatas = []

        if queues:
            for i in range(len(queues)):
                queues_data = {
                    "id": i,
                    "url": queues[i]
                }
                resdatas.append(queues_data)

            self.usego.sendlog(f'list结果：{resdatas}')
            res = ResMsg(data=resdatas)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'list没有数据：{queues}')
            res = ResMsg(code='B0001', msg='没有可用队列数据')
            responseData = res.to_json()

        return responseData

    def amazonSQS_delete(self):
        """删除指定的 SQS 队列"""
        data_request = request.json
        url = data_request.get('url')

        if not url:
            self.usego.sendlog(f"删除失败，未提供 URL 参数")
            res = ResMsg(code='B0002', msg="请求缺少必要的参数：url")
            return res.to_json()

        try:
            # 尝试删除队列
            self.aws_sqs.delFIFO(url)
            self.usego.sendlog(f'成功删除队列：{url}')
            res = ResMsg(data="成功删除队列")
            responseData = res.to_json()
        except Exception as e:
            # 捕获异常，防止系统崩溃
            self.usego.sendlog(f'删除队列失败：{e}')
            res = ResMsg(code='B0003', msg=f"删除队列失败：{str(e)}")
            responseData = res.to_json()

        return responseData
