# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/23 23:32
@Author ： eblis
@File ：mysqlDatabase.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import time

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import pymysql
from dbutils.pooled_db import PooledDB

import middleware.public.configurationCall as configCall

class mysqlGO():

    def article_mysql_connect(self):
        """
            @Datetime ： 2024/9/23 23:35
            @Author ：eblis
            @Motto：文章库
        """

        # 创建连接池
        pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=20,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=5,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的
            # connections和 cursors都不支持共享连接。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=1,
            # ping MySQL服务端，检查是否服务可用。如：0 = None = never, 1 = default = whenever it is requested,
            # 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=configCall.mysql_111_host,  # 主机名
            port=eval(configCall.mysql_111_port),  # 端口号，MySQL默认为3306
            user=configCall.mysql_111_account,  # 用户名
            password=configCall.mysql_111_password,  # 密码
            database=configCall.mysql_article_database,  # 数据库名称
            charset='utf8',
            # 添加超时参数
            connect_timeout=10,  # 连接超时时间，单位为秒
            read_timeout=30,  # 读取超时时间，单位为秒
            write_timeout=30  # 写入超时时间，单位为秒
        )
        # 连接 MySQL 数据库
        # conn = pymysql.connect(
        #     host=configCall.mysql_111_host,  # 主机名
        #     port=eval(configCall.mysql_111_port),  # 端口号，MySQL默认为3306
        #     user=configCall.mysql_111_account,  # 用户名
        #     password=configCall.mysql_111_password,  # 密码
        #     database=configCall.mysql_article_database,  # 数据库名称
        #
        # )
        # # 创建游标对象
        # cursor = conn.cursor()
        return pool


    def basis_mysql_connect(self):
        """
            @Datetime ： 2024/9/23 23:35
            @Author ：eblis
            @Motto：基础数据
        """
        # 创建连接池
        pool = PooledDB(
            creator=pymysql,
            maxconnections=50,  # 根据实际情况增加
            mincached=10,
            maxcached=10,
            maxshared=10,
            blocking=True,
            maxusage=None,
            setsession=[],
            ping=1,
            host=configCall.mysql_65_host,
            port=eval(configCall.mysql_65_port),
            user=configCall.mysql_65_account,
            password=configCall.mysql_65_password,
            database=configCall.mysql_base_database,
            charset='utf8',
            connect_timeout=10,  # 加入超时配置
            read_timeout=30,
            write_timeout=30
        )
        return pool

    def _connect(self, mo):
        """
            @Datetime ： 2024/10/9 12:48
            @Author ：eblis
            @Motto：从连接池中获取连接: article 是文章库，basis 是基础信息
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if mo == "article":
                    pool = self.article_mysql_connect()
                else:
                    pool = self.basis_mysql_connect()
                conn = pool.connection()
                return conn
            except Exception as e:
                print(f"Attempt {attempt + 1} - Failed to connect: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Optional: Wait before retrying
        return None  # Or raise an error

        # 归还连接到连接池

    def _close(self, conn, cursor):
        print("进来_close")
        if cursor:
            cursor.close()
        if conn:
            conn.close()


    def mysql_select(self, mo, selectSQL):
        # time.sleep(1)
        conn = self._connect(mo)
        if conn is None:
            print(f"conn 失败 ")
            return f"sql 语句异常"
        cursor = None
        try:
            cursor = conn.cursor()
            start_time = time.time()  # 记录开始时间
            cursor.execute(selectSQL)
            print("selectSQL", selectSQL)
            result = cursor.fetchall()
            end_time = time.time()  # 记录结束时间
            print(f"Query executed in {end_time - start_time:.2f} seconds")  # 打印查询耗时
            # print("result",result)

        except Exception as e:
            print(f"SQL语句异常: {e}")
            result = f"SQL语句异常: {e}"
        finally:
            self._close(conn, cursor)
        return result

    def mysql_select_special(self, mo, query, params):
        conn = self._connect(mo)
        if conn is None:
            print(f"conn 失败 ")
            return f"sql 语句异常"
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # print("selectSQL", selectSQL)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"sql 语句异常:{e}")
            return f"sql 语句异常:{e}"
        finally:
            self._close(conn, cursor)



    def mysql_commit(self, mo, commitSQL):
        conn = self._connect(mo)
        if conn is None:
            print(f"conn 失败 ")
            return f"sql 语句异常"

        cursor = None
        try:
            cursor = conn.cursor()
            result = cursor.execute(commitSQL)
            # print('result:', result)
            conn.commit()
        except Exception as e:
            print(f"sql 语句异常:{e}")
            result = f"sql 语句异常:{e}"

        finally:

            self._close(conn, cursor)

        return result

    def mysql_commit_tuple(self, mo, commitSQL, data):
        conn = self._connect(mo)
        if conn is None:
            print(f"conn 失败 ")
            result = f"sql 语句异常"
            return result
        cursor = None
        try:
            cursor = conn.cursor()
            result = cursor.execute(commitSQL, data)
            # print('result:', result)
            conn.commit()
        except Exception as e:
            print(f"sql 语句异常:{e}")
            result = f"sql 语句异常:{e}"
        finally:

            self._close(conn, cursor)

        return result

    def mysql_batch_commit(self,  mo, commitSQL, datalist):
        errdd = []
        conn = self._connect(mo)
        if conn is None:
            print(f"conn 失败 ")
            return f"sql 语句异常"
        cursor = None
        try:
            cursor = conn.cursor()
            print("开始执行sql")
            # 执行批量插入
            for data in datalist:
                try:
                    cursor.execute(commitSQL, data)
                except pymysql.err.IntegrityError as e:
                    # 如果遇到重复数据错误，跳过并继续执行
                    # print(f"重复数据错误: {e}")
                    errdd.append(data)
                    continue

            conn.commit()
            result = f"批量插入结束,跳过：{errdd}，已经存在"


        except Exception as e:

            print(f"sql 语句异常:{e}")
            result = f"sql 语句异常:{e}"

        finally:

            self._close(conn, cursor)

        return result

    def mysql_union_all(self, mo, commitSQL):
        conn = self._connect(mo)
        if conn is None:
            print(f"conn 失败 ")
            return f"sql 语句异常"
        cursor = None
        try:
            cursor = conn.cursor()
            # 设置最大长度以容纳生成的查询语句
            cursor.execute("SET SESSION group_concat_max_len = 1000000")
            # 生成查询语句
            cursor.execute(commitSQL)
            result = cursor.fetchone()

            sql_query = result[0]

            # result = sql_query
            # 准备并执行动态查询语句
            cursor.execute("PREPARE dynamic_statement FROM %s", sql_query)

            cursor.execute("EXECUTE dynamic_statement")
            # 获取查询结果
            query_result = cursor.fetchall()
            # 释放资源
            cursor.execute("DEALLOCATE PREPARE dynamic_statement")
            conn.commit()
            result = query_result  # 将查询结果存储在result中
        except Exception as e:
            print(f"sql 语句异常:{e}")
            result = f"sql 语句异常:{e}"
        finally:

            self._close(conn, cursor)

        return result



