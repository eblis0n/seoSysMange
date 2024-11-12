# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/25 21:56
@Author ： eblis
@File ：public_manage.py
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

class publicManage():
    def __init__(self):
        self.bp = Blueprint("public", __name__, url_prefix="/public")

        self.Myenum = MyEnum()


        self.bp.route(self.Myenum.PLATFORMS, methods=['GET'])(self.platforms)

    def platforms(self):

        platforms = [
            {
                "label": "telegra",
                "value": "telegra",
            },
            {
                "label": "blogger",
                "value": "blogger",
            },
        ]
        res = ResMsg(data=platforms)
        responseData = res.to_json()

        return responseData