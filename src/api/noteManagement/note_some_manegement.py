# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/1/11 14:59
@Author ： eblis
@File ：PcSettingsManagement.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
from datetime import datetime

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from src.public.new_sqlCollenction import new_sqlCollectionGO
from src.public.responseGO import ResMsg
from publicFunctions.commonUse import commonUse
from backstage.src.multiprocess.multiprocess import multiprocess
import publicFunctions.configuration as config
from backstage.src.articleAI.noteArticel import noteArticel
from backstage.src.jp_note.post_text_notes import notesTextPost



class noteSomeManage():
    def __init__(self):
        self.bp = Blueprint("noteSome", __name__, url_prefix="/note")
        self.ssql = new_sqlCollectionGO()
        self.Myenum = MyEnum()
        self.comm = commonUse()
        self.mul = multiprocess()
        self.noteArt = noteArticel()
        self.notesPost = notesTextPost()


        self.bp.route(self.Myenum.NOTE_USER_ARTICLE_POST_LIST, methods=['GET'])(self.note_user_article_post_list)
        self.bp.route(self.Myenum.NOTE_USER_ARTICLE_INSERT, methods=['POST'])(self.note_user_article_insert)
        self.bp.route(self.Myenum.NOTE_USER_Article_DEL, methods=['POST'])(self.note_user_article_del)





    def note_user_article_post_list(self):
        """
            @Datetime ： 2024/7/17 13:41
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.ssql.note_article_list_sql()

        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [
                    {'id': item[0], 'noteuser': item[1], 'keyword': item[2], 'title': item[3], 'content': item[4],
                     'url': item[5], 'create_at': self.comm.turn_isoformat(item[6]), 'update_at': self.comm.turn_isoformat(item[7])} for item in sql_data]
            except:
                self.comm.sendlog(f'list没数据：{sql_data}')
                res = ResMsg(code=10001, msg=f'list没数据：{sql_data}')
                responseData = res.to_json()
            else:
                self.comm.sendlog(f'list结果：{resdatas}')
                res = ResMsg(data=resdatas, total=len(resdatas))
                responseData = res.to_dict()

        else:
            self.comm.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code=10001, msg=f'list查询失败：{sql_data}')
            responseData = res.to_json()
        return responseData
    
    
    def note_user_article_insert(self):
        """
            @Datetime ： 2024/7/30 17:06
            @Author ：eblis
            @Motto：简单描述用途
        """

        form_data = request.json
        noteuser = form_data['noteuser']
        quantity = form_data['quantity']
        trade = form_data['trade']

        characters = noteuser.split("^")
        tasks_args = []
        # print(f"这次有{len(characters)} 需要{characters}执行")
        for i in range(len(characters)):
            character = characters[i].strip()
            output_folder = f"{config.note_path}/{character}"
            # self.note.run(character, int(quantity), output_folder)
            # character1 = character.encode('utf-8', errors='ignore').decode('utf-8')

            tasks_args.append((self.noteArt.run, (character, int(quantity), trade.strip(), output_folder)))

        self.mul.pro_task_go(self.mul.article_pool_go, (1, tasks_args))

        self.comm.sendlog(f'文章正在生成，大概需要1-10分钟')
        res = ResMsg(data=f'文章正在生成，大概需要1-10分钟')
        responseData = res.to_json()

        return responseData



    def note_user_article_del(self):
        """
            @Datetime ： 2024/7/30 17:06
            @Author ：eblis
            @Motto：简单描述用途
        """

        form_data = request.json
        id = form_data['id']


        sql_data = self.ssql.note_article_del(id)

        if "sql 语句异常" not in str(sql_data):
            self.comm.sendlog(f'删除成功：{sql_data}')
            #
            res = ResMsg(data=f'删除成功')
            responseData = res.to_dict()
        else:
            self.comm.sendlog(f'删除失败：{sql_data}')
            res = ResMsg(code=10001, msg=f'删除失败：{sql_data}')
            responseData = res.to_json()
        return responseData



