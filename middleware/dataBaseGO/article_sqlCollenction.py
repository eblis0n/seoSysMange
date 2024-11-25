# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/24 01:19
@Author ： eblis
@File ：article_sql_go.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from backendServices.unit.dataBase.mysqlDataBase import mysqlGO
from middleware.public.commonUse import otherUse

# 执行后不主动关闭数据库连接，通过 外部调用 关闭
class article_sqlGO():
    def __init__(self):
        self.ssql = mysqlGO()
        self.usego = otherUse()

    ############################################# 公共 #####################################################
  
    def ai_open_api_sql(self, keywords):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT `values`  FROM sys_settings  WHERE `keywords`  = '{keywords}';"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data

    ############################################# ai prompt #####################################################

    def ai_prompt_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_ai_prompt ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data

    def ai_prompt_select_sql(self, id):
        # noinspection SqlNoDataSourceInspection

        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_ai_prompt WHERE `id`  = '{id}';"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data

    def ai_prompt_insert_sql(self, salesman, sort, name, pronoun, prompt, create_at):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""INSERT INTO seo_ai_prompt (`salesman`,`sort`, `name`, `pronoun`,`prompt`,  `create_at`) VALUES ('{salesman}', '{sort}', '{name}', '{pronoun}','{prompt}', '{create_at}');"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

    def ai_prompt_delete_sql(self, id):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""DELETE FROM seo_ai_prompt WHERE `id` = '{id}';"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

    def ai_prompt_update_sql(self, salesman, sort, name, pronoun, prompt, id):
        """
            更新 PC 设置的状态、名称和地址
        """

        sqlgo = f"""
                        UPDATE seo_ai_prompt 
                        SET `salesman` = '{salesman}', `sort` = '{sort}', `name` = '{name}',`pronoun` = '{pronoun}', `prompt` = '{prompt}'
                        WHERE `id` = {id};
                    """
        # 执行 SQL 更新查询
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data


    ############################################# article #####################################################


    def article_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_article ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data

    def article_insert_sql(self, sortID, source, title, content, language, type, user, commission, create_at):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""INSERT INTO seo_article (`sortID`, `source`,`title`, `content`, `language`, `type`, `user`, `commission`,  `create_at`) VALUES ('{sortID}', '{source}','{title}',"{content}",'{language}','{type}','{user}','{commission}', '{create_at}');"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data


    def ai_article_insert_sql(self, promptID, sortID, source, title, content, language, type, user, commission, create_at):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""INSERT INTO seo_article (`promptID`,`sortID`, `source`,`title`, `content`, `language`,`type`, `user`, `commission`,  `create_at`) VALUES ('{promptID}', '{sortID}', '{source}','{title}',"{content}",'{language}','{type}','{user}','{commission}', '{create_at}');"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

    def article_delete_sql(self, id):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""DELETE FROM seo_article WHERE `id` = '{id}';"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

    # def article_update_sql(self, promptID, sortID, source, title, content, user, commission, id):
    #     """
    #         更新 PC 设置的状态、名称和地址
    #     """
    #
    #     sqlgo = f"""
    #                     UPDATE seo_ai_prompt
    #                     SET `promptID` = '{promptID}', `sortID` = '{sortID}', `source` = '{source}', `title` = '{title}', `content` = '{content}', `user` = '{user}', `commission` = '{commission}'
    #                     WHERE `id` = {id};
    #                 """
    #     # 执行 SQL 更新查询
    #     sql_data = self.ssql.mysql_commit('article', sqlgo)
    #     return sql_data
    #



############################################# category #####################################################

    def category_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_sort ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data

    def category_insert_sql(self, name, level, create_at):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""INSERT INTO seo_sort (`name`,`level`, `create_at`) VALUES ('{name}','{level}','{create_at}');"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

    def category_delete_sql(self, id):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""DELETE FROM seo_sort WHERE `id` = '{id}';"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

    def category_update_sql(self, name, level, id):
        """
            更新 PC 设置的状态、名称和地址
        """

        sqlgo = f"""
                           UPDATE seo_sort 
                           SET  `name` = '{name}', `level` = '{level}'
                           WHERE `id` = '{id}';
                       """
        # 执行 SQL 更新查询
        sql_data = self.ssql.mysql_commit('article', sqlgo)
        return sql_data

