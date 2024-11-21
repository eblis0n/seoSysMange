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
base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from datetime import datetime
from middleware.public.returnMsg import ResMsg

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.public.commonUse import otherUse


class aiPromptManage():
    def __init__(self):
        self.bp = Blueprint("aiPrompt", __name__, url_prefix="/prompt")
        self.Myenum = MyEnum()

        self.ssql = article_sqlGO()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.AI_PROMPT_INSERT, methods=['POST'])(self.ai_prompt_insert)
        self.bp.route(self.Myenum.AI_PROMPT_DELETE, methods=['POST'])(self.ai_prompt_delete)
        self.bp.route(self.Myenum.AI_PROMPT_UPDATE, methods=['POST'])(self.ai_prompt_update)
        self.bp.route(self.Myenum.AI_PROMPT_LIST, methods=['GET'])(self.ai_prompt_list)


    def ai_prompt_insert(self):

        data_request = request.json
        salesman = data_request['salesman']
        sort = data_request['sort']
        pronoun = data_request['pronoun']
        prompt = data_request['prompt']
        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # converted_prompt = prompt.replace("'", '"')
        print("prompt",prompt)
        # print("pronoun", pronoun)
        # print("sort",sort)
        sql_data = self.ssql.ai_prompt_insert_sql(salesman, sort, pronoun, prompt, create_at)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'添加成功：{sql_data}')
            res = ResMsg(data=sql_data)
        else:
            self.usego.sendlog(f'添加失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'添加失败：{sql_data}')

        return res.to_json()



    def ai_prompt_delete(self):

        data_request = request.json
        id = data_request['id']

        sql_data = self.ssql.ai_prompt_delete_sql(id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'成功删除：{id}')
            res = ResMsg(data=sql_data)

        else:
            self.usego.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'删除失败：{sql_data}')

        return res.to_json()


    def ai_prompt_update(self):

        data_request = request.json
        id = data_request['id']
        salesman = data_request['salesman']
        sort = data_request['sort']
        pronoun = data_request['pronoun']
        prompt = data_request['prompt']



        sql_data = self.ssql.ai_prompt_update_sql(salesman, sort, pronoun, prompt, id)

        if "sql 语句异常" not in str(sql_data):
            self.usego.sendlog(f'更新成功：{sql_data}')
            res = ResMsg(data=sql_data)


        else:
            self.usego.sendlog(f'更新失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'更新失败：{sql_data}')

        return res.to_json()

    def ai_prompt_list(self):
        sql_data = self.ssql.ai_prompt_list_sql()
        # print("sql_data", sql_data)

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'salesman': item[1], 'sort': item[2], 'pronoun': item[3], 'prompt': item[4], 'create_at': self.usego.turn_isoformat(item[5]), 'update_at': self.usego.turn_isoformat(item[6])} for item in sql_data]

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

