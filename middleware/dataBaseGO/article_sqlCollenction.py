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

    def article_select_sql(self, limit=None, sortID=None, type=None, source=None, commission=None, isAI=None,user=None):
        """
            @Datetime ： 2024/5/7 10:59
            @Author ：eblis
            @Motto：查文章
        """
        # 构建参数字典，过滤掉 None 和空字符串
        params = {k: v for k, v in locals().items() if
                  k in ['commission', 'isAI', 'sortID', 'type', 'source', 'user'] and v not in [None, ""]}
        print("非 None 的参数名：", list(params.keys()))

        # 构建基础 SQL
        sql = "SELECT * FROM seo_article"
        where_clauses = []

        # 构建 WHERE 条件
        for key, value in params.items():
            if isinstance(value, str):
                escaped_value = value.replace("'", "\\'")
                where_clauses.append(f"`{key}` = '{escaped_value}'")
            else:
                where_clauses.append(f"`{key}` = {value}")

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        # 添加排序和限制
        sql += " ORDER BY `create_at` ASC"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"  # 确保 limit 是整数
        print("sql", sql)

        sql_data = self.ssql.mysql_select('article', sql)
        return sql_data


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



    ############################################# post article history #################################################

    def post_article_history_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_article_post_history ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data


    def post_articlehistory_batch_insert(self, datalist):
        # datalist 是 list  里有 N 组 元组
        commitSQL = """
            INSERT INTO seo_article_post_history (articleID, accountID, platform, url, created_at)
            VALUES (%s, %s,%s, %s, %s)
            """
        print(f"post_articlehistory_batch_insert:{commitSQL}")
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_batch_commit('article', commitSQL, datalist)
        return sql_data

    ############################################# post article_result #################################################

    def post_article_result_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_result_article_links ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('article', sqlgo)
        return sql_data

    def post_article_result_batch_insert(self, datalist):
        # datalist 是 list  里有 N 组 元组
        commitSQL = """
            INSERT INTO seo_result_article_links (platform, url, created_at)
            VALUES (%s, %s, %s)
            """
        # 执行 SQL 查询语句
        print("post_article_result_batch_insert",commitSQL)
        sql_data = self.ssql.mysql_batch_commit('article', commitSQL, datalist)
        return sql_data


