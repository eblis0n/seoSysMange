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
from backendServices.src.awsMQ.amazonSQS import AmazonSQS


class splicingManage():
    def __init__(self):
        self.bp = Blueprint("splicing", __name__, url_prefix="/splicing")
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.tele = telegraSelenium()

        
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

        if "sql 语句异常" in str(sql_data):
            self.usego.sendlog(f'没有可用的客户端：{sql_data}')
            res = ResMsg(code='B0001', msg=f'没有可用的客户端')
            return res.to_json()

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

        if not resdatas:
            self.usego.sendlog(f'没有可用的客户端{resdatas}')
            res = ResMsg(code='B0001', msg=f'没有可用的客户端')
            return res.to_json()

        self.usego.sendlog(f'有 {len(resdatas)} 设备符合')
        aws = AmazonSQS()
        results = []
        for idx, client in enumerate(resdatas):
            result = {}
            response = aws.initialization(f'client_{client["name"]}')
            queue_url = response['QueueUrl']
            print("queue_url", queue_url)

            task_data = {
                'command': 'run_telegra_selenium',
                'genre': genre,
                'platform': platform,
                'alt_text': alt_text,
                'stacking_min': stacking_min,
                'stacking_max': stacking_max,
            }
            response = aws.sendMSG(queue_url, "run_telegra_group", "run_telegra_selenium", task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_telegra_selenium，任务发送结果:{response}')
        res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        return res.to_json()






