# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 16:31
@Author ： eblis
@File ：outcome_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse
from middleware.public.returnMsg import ResMsg
from backendServices.src.assistance.spliceGo import spliceGo
from middleware.control.taskAws import taskAws


class splicingManage():
    def __init__(self):
        self.bp = Blueprint("splicing", __name__, url_prefix="/splicing")
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.task = taskAws()




        self.bp.route(self.Myenum.SPLICING_SUBMIT_PUSH, methods=['POST'])(self.splicing_submit_push)
        self.bp.route(self.Myenum.SPLICING_INSERT, methods=['POST'])(self.splicing_insert)
        self.bp.route(self.Myenum.SPLICING_LIST, methods=['GET'])(self.splicing_list)
        self.bp.route(self.Myenum.SPLICING_TOTAL, methods=['GET'])(self.splicing_total)
        self.bp.route(self.Myenum.SPLICING_DELETE_ALL, methods=['GET'])(self.splicing_delete_all)


    def splicing_list(self):
        """
            @Datetime ： 2024/10/21 00:28
            @Author ：eblis
            @Motto：简单描述用途
        """
        try:
            sql_data = self.mossql.splicing_interim_findAll("seo_external_links_post", end=10000)
        except Exception as e:
            self.usego.sendlog(f'list查询失败：{e}')
            sql_data = None

        resdatas = []

        if sql_data is not None:
            if len(sql_data) > 0:
                for i in range(len(sql_data)):
                    thisdata = {
                        "id": i,
                        "url": sql_data[i]["url"],
                        "platform": sql_data[i]["platform"],
                        "genre": sql_data[i]["genre"],
                        "sort": sql_data[i]["sort"],
                        "create_at": self.usego.turn_isoformat(sql_data[i]["create_at"])
                    }
                    resdatas.append(thisdata)

                self.usego.sendlog(f'list结果：{len(resdatas)}')
                res = ResMsg(data=resdatas)

            else:
                self.usego.sendlog(f'list结果：{len(resdatas)}')
                res = ResMsg(data=resdatas)

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败')


        return res.to_json()

    def splicing_insert(self):

        data_request = request.json

        url = data_request['url']
        genre = data_request['genre']
        platform = data_request['platform']
        sort = data_request['sort']

        url_list = url.split("\n")
        spl = spliceGo()

        try:
            zyurl = data_request['zyurl']

        except:
            self.usego.sendlog(f'自成一派')
            result = spl.splice_301(sort, genre, platform, url_list)
        else:
            if zyurl == "":
                result = spl.splice_301(sort, genre, platform, url_list)
            else:
                zyurl_list = zyurl.split("\n")
                result = spl.splice_301(sort, genre, platform, url_list, zyurl_list)

        if result is not None:
            self.usego.sendlog(f'添加成功：{result}')
            res = ResMsg(data=result)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'入库失败')
            res = ResMsg(code='B0001', msg=f'入库失败')
            responseData = res.to_json()

        return responseData

    def splicing_submit_push(self):
        """
                    @Datetime ： 2024/10/21 00:28
                    @Author ：eblis
                    @Motto：Amazon SQS 不能接收 过长 消息，大量执行，查数据库 放在脚本上，不能从队列传送
                """
        data_request = request.json

        datasDict = {
            "title_alt": data_request['title_alt'],
            "alt_text": data_request['alt_text'],
            "stacking_min": data_request['stacking_min'],
            "stacking_max": data_request['stacking_max'],
            "genre": data_request['genre'],
            "platform": data_request['platform'],
            "postingStyle": data_request['postingStyle'],
            "group": data_request['group'],
            "sort": data_request['sort'],
            "isarts": data_request['isarts']
        }
        self.usego.sendlog(f"接收到的参数：{datasDict}")
        results = self.task.run("splice", datasDict["platform"], datasDict)

        res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        return res.to_json()


    def splicing_total(self):
        """
        @Datetime ： 2024/10/28 16:50
        @Author ：eblis
        @Motto：根据默认平台查询总数
        """

        def get_platform_data(platform):
            """根据平台名称查询数据"""
            query = {"platform": platform}
            try:
                return self.mossql.splicing_interim_find_count("seo_external_links_post", query)
            except Exception as e:
                self.usego.sendlog(f"查询 {platform} 数据失败：{e}")
                return 0

        # 默认平台列表
        platforms = ["blogger", "telegra", "note"]

        # 查询每个平台的数据
        results = {}
        for platform in platforms:
            results[f"{platform}_total"] = get_platform_data(platform)
        #
        # datas = [results]



        # 输出日志
        self.usego.sendlog(f"查询结果：{results}")

        # 构建返回数据
        res = ResMsg(data=results)
        return res.to_json()



    def splicing_delete_all(self):
        sql_data = self.mossql.splicing_interim_delet("seo_external_links_post", query=None, multiple=False, clear_all=True)
        self.usego.sendlog(f'删除结果：{sql_data}')
        res = ResMsg(data=sql_data)
        return res.to_json()
    
    

    















