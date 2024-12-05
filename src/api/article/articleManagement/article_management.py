# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/1/11 14:59
@Author ： eblis
@File ：pc_settings_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
from datetime import datetime

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.public.returnMsg import ResMsg

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.public.commonUse import otherUse
from middleware.control.taskAws import taskAws

class articleManage():
    def __init__(self):
        self.bp = Blueprint("article", __name__, url_prefix="/article")
        self.Myenum = MyEnum()

        self.artsql = article_sqlGO()
        self.usego = otherUse()
        self.task = taskAws()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.ARTICLE_INSERT, methods=['POST'])(self.article_insert)
        self.bp.route(self.Myenum.ARTICLE_DELETE, methods=['POST'])(self.article_delete)
        self.bp.route(self.Myenum.ARTICLE_LIST, methods=['GET'])(self.article_list)

        self.bp.route(self.Myenum.POST_IN_SQL, methods=['POST'])(self.post_in_sql)


    def article_insert(self):
        data_request = request.json
        sortID = data_request['sortID']
        commission = data_request['commission']
        type = data_request['type']
        source = data_request['source']

        # 处理 commission 为 0 或 "0" 时，确保 user 为列表
        user_l = []
        if commission == 0 or commission == "0":
            user_l.append(data_request['user'])
        else:
            user = ""

        # 如果 isAI == 0，处理相关字段
        if int(data_request['isAI']) == 0:
            self.usego.sendlog(f'要发 AI 文章哦，')
            promptID = data_request['promptID']
            self.usego.sendlog(f'promptID:{promptID}')

            # 处理主题字段，确保为空时返回空列表
            theme = data_request.get('theme', "")
            theme_l = theme.split("^") if theme else []

            # 处理关键词字段
            Keywords = data_request.get('Keywords', "")
            Keywords_l = Keywords.split("^") if Keywords else []

            # 处理标签字段
            ATag = data_request.get('ATag', "")
            ATag_l = ATag.split("^") if ATag else []

            # 处理链接字段
            link = data_request.get('link', "")
            link_l = link.split("^") if link else []

            # 处理语言字段
            language = data_request.get('language', "")
            language_l = language.split("^") if language else []


            # 构建数据字典
            datasDict = {
                "platform": "article",
                "max_length": 0,
                "source": source,
                "type": type,
                "promptID": promptID,
                "sortID": sortID,
                "theme": theme_l,
                "Keywords": Keywords_l,
                "ATag": ATag_l,
                "link": link_l,
                "language": language_l,
                "user": user_l,
            }
            max_length = max((len(lst) for lst in datasDict.values() if isinstance(lst, list) and lst), default=0)
            datasDict["max_length"] = max_length

            if max_length != 0:
                self.usego.sendlog(f'datasDict：{max_length}，{datasDict}')

                # 修改每个字段
                for key, val in datasDict.items():
                    if isinstance(val, list):  # 确保 val 是列表
                        if val:  # 列表非空
                            datasDict[key] = (val * (max_length // len(val) + 1))[:max_length]
                        else:  # 列表为空
                            datasDict[key] = []
                    else:  # 非列表字段
                        continue

            self.usego.sendlog(f"接收到的参数：{datasDict}")
            results = self.task.run("article", datasDict["platform"], datasDict)
            res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        else:
            # 处理 isAI != 0 的情况
            language = data_request['spoken']
            create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = data_request['title']
            content = data_request['content']

            sql_data = self.artsql.article_insert_sql(sortID, source, title, content, language, type, user_l, commission,
                                                    create_at)
            if "sql 语句异常" not in str(sql_data):
                self.usego.sendlog(f'添加成功：{sql_data}')
                res = ResMsg(data=sql_data)
            else:
                self.usego.sendlog(f'添加失败：{sql_data}')
                res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()

    def article_delete(self):

        data_request = request.json
        id = data_request['id']

        sql_data = self.artsql.article_delete_sql(id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def article_list(self):

        sql_data = self.artsql.article_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'isAI': item[1], 'promptID': item[2],  'sortID': item[3], 'source': item[4], 'title': item[5], 'content': item[6], 'type': item[7], 'user': item[8], 'commission': item[9], 'language': item[10], 'create_at': self.usego.turn_isoformat(item[11]), 'update_at': self.usego.turn_isoformat(item[12])} for item in sql_data]

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



    def post_in_sql(self):
        """
            @Datetime ： 2024/11/24 23:53
            @Author ：eblis
            @Motto：简单描述用途
        """
        data_request = request.json
        commission = data_request['commission']
        if commission == 0 or commission == "0":
            user = [data_request['user']]
        else:
            user = ""

        datasDict = {
            "platform": data_request['platform'],
            "group": "all",
            "post_max": 0,
            "sortID": data_request['sortID'],
            "type": data_request['type'],
            "commission": commission,
            "isAI": data_request['isAI'],
            "user": user,
            "language": data_request['spoken'],
            "isSecondary": data_request['isSecondary']
        }
        group = data_request['group']
        post_max = data_request['post_max']
        if int(post_max) != "":
            datasDict["post_max"] = int(post_max)
        if group == "":
            datasDict["group"] = "all"


        self.usego.sendlog(f"接收到的参数：{datasDict}")
        results = self.task.run("postSqlArticle", datasDict["platform"], datasDict)

        res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        return res.to_json()



