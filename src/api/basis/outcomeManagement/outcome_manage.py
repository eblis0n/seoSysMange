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
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.public.commonUse import otherUse
from middleware.public.returnMsg import ResMsg




class outcomeManage():
    def __init__(self):
        self.bp = Blueprint("outcome", __name__, url_prefix="/outcome")
        self.mossql = mongo_sqlGO()
        self.artsql = article_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()




        self.bp.route(self.Myenum.OUTCOME_LIST, methods=['GET'])(self.outcome_list)
        self.bp.route(self.Myenum.OUTCOME_TOTAL, methods=['GET'])(self.outcome_total)
        self.bp.route(self.Myenum.OUTCOME_DELETE_DATA, methods=['DELETE'])(self.outcome_delete_data)




    def outcome_list(self):
        """
            @Datetime ： 2024/10/21 00:28
            @Author ：eblis
            @Motto：telegra  的 拼接发布结果
        """
        platform = request.args.get('platform')
        # print("platform", platform)

        if platform is not None:
            if platform == "article":
                sql_data = self.artsql.post_article_result_list_sql()
                if "sql 语句异常" not in str(sql_data):
                    try:
                        resdatas = [{'id': item[0], 'platform': item[1], 'url': item[2], 'create_at': self.usego.turn_isoformat(item[3])} for item in sql_data]

                    except:
                        self.usego.sendlog(f'list没数据：{sql_data}')
                        res = ResMsg(code='B0001', msg=f'list没数据：{sql_data}')

                    else:
                        self.usego.sendlog(f'list结果：{resdatas}')
                        res = ResMsg(data=resdatas)


                else:
                    self.usego.sendlog(f'list查询失败：{sql_data}')
                    res = ResMsg(code='B0001', msg=f'list查询失败：{sql_data}')

                return res.to_json()


            else:

                try:
                    query = {
                        "platform": str(platform),
                    }
                    sql_data = self.mossql.splicing_interim_findAll("seo_result_301_links", query)
                except Exception as e:
                    self.usego.sendlog(f'list查询失败：{e}')
                    sql_data = None


                resdatas = []
                # print("sql_data", sql_data)
                if sql_data is not None:
                    if len(sql_data) > 0:
                        for i in range(len(sql_data)):
                            thisdata = {
                                "id": i,
                                "url": sql_data[i]["url"],
                                "platform": sql_data[i]["platform"],
                                "genre": sql_data[i]["genre"],
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
        else:
            self.usego.sendlog(f'缺少 platform 参数')
            return ResMsg(code='B0001', msg="缺少 platform  参数").to_json()


    def outcome_total(self):
        """
            @Datetime ： 2024/10/28 16:50
            @Author ：eblis
            @Motto：简单描述用途
        """
        platform = request.args.get('platform')

        if platform is not None:
            if platform == "article":
                # sql_data = self.artsql.post_article_result_list_sql()
                self.usego.sendlog(f'article 没开发')
                sql_data = 0
            else:
                try:
                    query = {
                        "platform": platform
                    }
                    sql_data = self.mossql.splicing_interim_find_count("seo_result_301_links", query)
                    self.usego.sendlog(f'查询结果：{sql_data}')
                except Exception as e:
                    self.usego.sendlog(f'list查询失败：{e}')
                    sql_data = 0

            datas = {
                "total": sql_data,
            }
            res = ResMsg(data=datas)
            return res.to_json()
        else:
            self.usego.sendlog(f'缺少 platform 参数')
            return ResMsg(code=400, msg="缺少 platform  参数").to_json()


    def outcome_delete_data(self):
        data_request = request.json  # 从 POST 请求体中获取参数
        platform = data_request.get('platform')  # 获取 platform 参数
        urldatas = data_request.get('urldatas')  # 获取 listdata 参数
        url_list = urldatas.split(",")

        if platform and urldatas:
            if platform == "article":

                sql_data = self.artsql.post_article_result_delete(url_list)
                if "sql 语句异常" not in str(sql_data):
                    self.usego.sendlog(f'成功删除：{url_list}')
                    res = ResMsg(data=sql_data)
                else:
                    self.usego.sendlog(f'删除失败：{sql_data}')
                    res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')
            else:

                query = {"platform": platform, "url": {"$in": url_list}}
                # 调用数据库删除方法
                sql_data = self.mossql.splicing_interim_delet(
                    "seo_result_301_links", query=query, multiple=True, clear_all=False
                )
                self.usego.sendlog(f'删除结果：{sql_data}')
                res = ResMsg(data=sql_data)
            return res.to_json()
        else:
            self.usego.sendlog(f'缺少 platform 或 listdata 参数')
            return ResMsg(code=400, msg="缺少 platform 或 listdata 参数").to_json()


