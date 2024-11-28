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
import middleware.public.configurationCall as configCall
from backendServices.src.googleOnline.google_online_excel_public import googleOnlinePublic
class publicManage():
    def __init__(self):
        self.bp = Blueprint("public", __name__, url_prefix="/public")

        self.Myenum = MyEnum()

        self.googlePublic = googleOnlinePublic()


        self.bp.route(self.Myenum.PLATFORMS, methods=['GET'])(self.platforms)
        self.bp.route(self.Myenum.GOOGLEEXCEL, methods=['GET'])(self.googleExcel)

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
            {
                "label": "note",
                "value": "note",
            },
            {
                "label": "article",
                "value": "article",
            },
        ]
        res = ResMsg(data=platforms)
        responseData = res.to_json()

        return responseData


    def googleExcel(self):

        shareURL = {}

        shareURL["url"] = configCall.google_docs_url.replace("edit?gid=0#gid=0", "preview")

        res = ResMsg(data=[shareURL])
        responseData = res.to_json()

        return responseData


