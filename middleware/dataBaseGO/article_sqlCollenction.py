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
class article_sqlCollectionGO():
    def __init__(self):
        self.ssql = mysqlGO()
        self.usego = otherUse()

    ############################################# 公共 #####################################################
  


    ############################################# 文章分组 #####################################################

    def article_group_list(self):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：文章分组
        """
        sqlgo = f"""
                                    SELECT /*+ NOCACHE */* FROM article_group ORDER BY create_at desc;
                                """
        # print("sqlgo", sqlgo)
        sql_data = self.ssql.mysql_select("article", sqlgo)
        return sql_data


    def article_group_insert(self, name, level, create_at):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：添加分组
        """
        datas = (name, level, create_at)
        sqlgo = f"""
                            INSERT INTO article_group (`name`, `level`, `create_at`) VALUES (%s, %s, %s, );
                            """
        # print("sqlgo", sqlgo)
        sql_data = self.ssql.mysql_commit_tuple("article", sqlgo, datas)

        return sql_data

    def article_group_update(self, id, name, level):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：更新分组
        """
        sqlgo = f""" UPDATE article_group SET `name`='{name}', `level`='{level}' WHERE `id` = '{id}';"""

        # print("sqlgo", sqlgo)
        sql_data = self.ssql.mysql_commit("article", sqlgo)
        return sql_data

    def article_group_del(self, id):
        """
            @Datetime ： 2024/8/20 14:13
            @Author ：eblis
            @Motto：简单描述用途
        """
        sqlgo = f"""DELETE FROM article_group WHERE `id` = '{id}';"""
        sql_data = self.ssql.mysql_commit("article", sqlgo)

        return sql_data


    ############################################# 文章 #####################################################

    def article_list(self):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：文章列表
        """
        sqlgo = f"""
                                    SELECT /*+ NOCACHE */* FROM article_manage ORDER BY create_at desc;
                                """
        # print("sqlgo", sqlgo)
        sql_data = self.ssql.mysql_select("article", sqlgo)
        return sql_data


    def article_insert(self, title, content, category, source, source_msg, customized, create_at):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：添加文章到
        """
        datas = (title, content, category, source, source_msg, customized, create_at)
        sqlgo = f"""
                            INSERT INTO article_manage (`title`, `content`,`category`,`source`, `source_msg`, `customized`,`create_at`) VALUES (%s, %s, %s, %s, %s, %s, %s );
                            """
        # print("sqlgo", sqlgo)
        sql_data = self.ssql.mysql_commit_tuple("article", sqlgo, datas)

        return sql_data


    def article_del(self, id):
        """
            @Datetime ： 2024/8/20 14:13
            @Author ：eblis
            @Motto：简单描述用途
        """
        sqlgo = f"""DELETE FROM article_manage WHERE `id` = '{id}';"""
        sql_data = self.ssql.mysql_commit("article", sqlgo)

        return sql_data

