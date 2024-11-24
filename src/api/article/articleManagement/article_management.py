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

        self.ssql = article_sqlGO()
        self.usego = otherUse()
        self.task = taskAws()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.ARTICLE_INSERT, methods=['POST'])(self.article_insert)
        self.bp.route(self.Myenum.ARTICLE_DELETE, methods=['POST'])(self.article_delete)
        # self.bp.route(self.Myenum.ARTICLE_UPDATE, methods=['POST'])(self.article_update)
        self.bp.route(self.Myenum.ARTICLE_LIST, methods=['GET'])(self.article_list)


    def article_insert(self):

        data_request = request.json
        sortID = data_request['sortID']
        commission = data_request['commission']
        type = data_request['type']
        source = data_request['source']

        if commission == 0 or commission == "0":
            user = [data_request['user']]
        else:
            user = ""

        if int(data_request['isAI']) == 0:
            promptID = data_request['promptID']
            try:
                theme = data_request['theme']
                theme_l = theme.split("^")
            except:
                theme_l = ""

            try:
                Keywords = data_request['Keywords']
                Keywords_l = Keywords.split("^")
            except:
                Keywords_l = ""

            try:
                ATag = data_request['ATag']
                ATag_l = ATag.split("^")
            except:
                ATag_l = ""
            try:
                link = data_request['link']
                link_l = link.split("^")
            except:
                link_l = ""

            try:
                language = data_request['language']
                language_l = language.split("^")
            except:
                language_l = ""

                # 获取每个列表的长度

            valid_lists = [lst for lst in [theme_l, Keywords_l, link_l, ATag_l, language_l, user] if
                           lst !=""]
            max_length = max([len(lst) for lst in valid_lists], default=0)
            # 找出最大长度
            datasDict = {
                "platform": "blogger",
                "max_length": max_length,
                "promptID": promptID,
                "sortID": sortID,
                "source": source,
                "type": type,
                "theme": [],
                "Keywords": [],
                "link": [],
                "ATag": [],
                "language": [],
                "user": [],
            }
            if max_length != 0:
                # 输出结果
                self.usego.sendlog(f'本次批量：{max_length}')
                # 使每个列表达到最大长度
                aligned_lists = [(lst * (max_length // len(lst) + 1))[:max_length] for lst in valid_lists]
                new_theme_l, new_Keywords_l, new_link_l, new_ATag_l, new_language_l, new_user_l = aligned_lists
                datasDict["theme"].extend(new_theme_l)  # 追加而不是替换
                datasDict["Keywords"].extend(new_Keywords_l)
                datasDict["link"].extend(new_link_l)
                datasDict["ATag"].extend(new_ATag_l)
                datasDict["language"].extend(new_language_l)
                datasDict["user"].extend(new_user_l)

            self.usego.sendlog(f"接收到的参数：{datasDict}")
            results = self.task.run("article", datasDict["platform"], datasDict)
            res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        else:
            create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = data_request['title']
            content = data_request['content']

            sql_data = self.ssql.article_insert_sql(sortID, source, title, content, type, user, commission, create_at)
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

        sql_data = self.ssql.article_delete_sql(id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def article_list(self):
        sql_data = self.ssql.article_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'isAI': item[1],'promptID': item[2],  'sortID': item[3], 'source': item[4], 'title': item[5], 'content': item[6], 'type': item[7], 'user': item[8], 'commission': item[9], 'create_at': self.usego.turn_isoformat(item[10]), 'update_at': self.usego.turn_isoformat(item[11])} for item in sql_data]

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

