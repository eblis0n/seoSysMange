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


# 执行后不主动关闭数据库连接，通过 外部调用 关闭
class basis_sqlGO():
    def __init__(self):
        self.ssql = mysqlGO()
        # self.conn, self.cursor = self.ssql.basis_mysql_connect()
        # self.usego = otherUse()

    ############################################# 公共 #####################################################



    ############################################# 后台管理用户信息 #####################################################

    def sys_user_list(self):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：文章分组
        """
        sqlgo = f"""
                                    SELECT /*+ NOCACHE */* FROM sys_user ;
                                """
        # print("sqlgo", sqlgo)
        sql_data = self.ssql.mysql_select('basis', sqlgo)

        return sql_data

    def sys_user_info_select(self, username=None, password=None, id=None):
        """
            @Datetime ： 2024/9/24 01:28
            @Author ：eblis
            @Motto：文章分组
        """
        params = {k: v for k, v in locals().items() if
                  k in ['username', 'password', 'id'] and v is not None and v != ""}
        print("非 None 的参数名：", list(params.keys()))
        if params:
            conditions = [f"`{k}` = '{v}'" for k, v in params.items()]
            sqlgo = f"SELECT /*+ NOCACHE */* FROM sys_user where {' and '.join(conditions)};"
            sql_data = self.ssql.mysql_select('basis', sqlgo)
            return sql_data
        else:
            print("没有有效的查询参数")
            return None

    # def sys_user_info_select(self, username=None, password=None, id=None):
    #     """
    #         @Datetime ： 2024/9/24 01:28
    #         @Author ：eblis
    #         @Motto：文章分组
    #     """
    #     non_none_params = []
    #     for kk, val in locals().items():
    #         if kk in ['username', 'password', 'id']:
    #             if val is not None:
    #                 if val != "":
    #                     non_none_params.append(kk)
    #     print("非 None 的参数名：", non_none_params)
    #     if len(non_none_params) == 3:
    #         one = non_none_params[0].replace('"', '')
    #         two = non_none_params[1].replace('"', '')
    #         three = non_none_params[2].replace('"', '')
    #         sqlgo = f"""
    #                         SELECT /*+ NOCACHE */* FROM sys_user where `{one}` = '{locals()[non_none_params[0]]}' and `{two}` = '{locals()[non_none_params[1]]}' and `{three}` = '{locals()[non_none_params[2]]}';
    #                 """
    #     elif len(non_none_params) == 2:
    #             one = non_none_params[0].replace('"', '')
    #             two = non_none_params[1].replace('"', '')
    #             sqlgo = f"""
    #                         SELECT /*+ NOCACHE */* FROM sys_user where `{one}` = '{locals()[non_none_params[0]]}' and `{two}` = '{locals()[non_none_params[1]]}' ;
    #                     """
    #     else:
    #         one = non_none_params[0].replace('"', '')
    #         sqlgo = f"""
    #                     SELECT /*+ NOCACHE */* FROM sys_user where `{one}` = '{locals()[non_none_params[0]]}';
    #                 """
    #     # print("sqlgo",sqlgo)
    #     sql_data = self.ssql.mysql_select('basis',  sqlgo)
    #
    #     return sql_data
    
    # def sys_user_login():
    #     """
    #         @Datetime ： 2024/10/9 13:51
    #         @Author ：eblis
    #         @Motto：简单描述用途
    #     """
    

    def sys_user_perm_select(self, user_id):

        sqlgo = f"""
            SELECT
                uu.id AS user_id,
                uu.username,
                uu.nickname,
                uu.avatar,
                ro.`name`AS role,
                mm.perm AS perm

            FROM
                sys_user uu
                LEFT JOIN sys_user_role uro ON uu.id = uro.user_id
                LEFT JOIN sys_role ro ON uro.role_id = ro.id
                LEFT JOIN sys_role_menu me ON ro.id = me.role_id 
                LEFT JOIN sys_menu mm on me.menu_id = mm.id
            WHERE
                uu.id = '{user_id}' AND mm.perm is not NULL;
        """
        sql_data = self.ssql.mysql_select('basis', sqlgo)

        return sql_data



    def sys_user_router_code_select(self, user_id):
        """∑
           @Datetime ： 2024/9/24 01:28
           @Author ：eblis
           @Motto： 查用户获取code
        """
        sqlgo = f"""
                    SELECT `code` FROM sys_role ro INNER JOIN sys_user_role uro ON uro.role_id = ro.id
	WHERE uro.user_id = {user_id}
                """
        sql_data = self.ssql.mysql_select('basis', sqlgo)

        return sql_data

    # ############################################# 菜单 #####################################################

    def menu_list(self):
        """
            @Datetime ： 2024/10/23 22:51
            @Author ：eblis
            @Motto：简单描述用途
        """
        sqlgo = f""" SELECT * FROM sys_menu; """

        sql_data = self.ssql.mysql_select('basis', sqlgo)
        return sql_data



    def menu_router_list(self, roles, button_value):
        """
            @Datetime ： 2024/9/30 15:43
            @Author ：eblis
            @Motto：将非按钮类的 菜单
        """
        roles_condition = ""
        if roles and len(roles) > 0 and 'ROOT' not in roles:
            # roles_tuple = tuple(roles)
            # roles_condition = f"AND t3.code IN {roles_tuple}"
            roles_condition = "AND t3.code IN (" + ', '.join(f"'{role}'" for role in roles) + ")"

        # Base query
        sqlgo = f"""
            SELECT DISTINCT
            t1.id, t1.name, t1.parent_id, t1.route_name, t1.route_path, t1.component, t1.icon, t1.sort, t1.visible, t1.redirect, t1.type, t1.always_show, t1.keep_alive, t1.params
        FROM
            sys_menu t1
        INNER JOIN
            sys_role_menu t2 ON t1.id = t2.menu_id
        INNER JOIN
            sys_role t3 ON t2.role_id = t3.id AND t3.status = 1 AND t3.is_deleted = 0
        WHERE
            t1.type != {button_value}
            {roles_condition}
        ORDER BY
            t1.sort
        """

        sql_data = self.ssql.mysql_select('basis', sqlgo)
        return sql_data

    ############################################# pc_management #####################################################

    def pcSettings_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM pro_pc_settings ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('basis', sqlgo)
        return sql_data

    def pcSettings_insert_sql(self, group, name, address, account, password, platform, remark, create_at):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""INSERT INTO pro_pc_settings (`group`, `name`, `address`,`account`, `password`,`platform`, `remark`,`create_at`) VALUES ('{group}','{name}', '{address}', '{account}', '{password}',  '{platform}', '{remark}','{create_at}');"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data

    def pcSettings_delete_sql(self, id):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""DELETE FROM pro_pc_settings WHERE id = {id};"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data

    def pcSettings_update_sql(self, group, name, address, account, password, platform, remark, state, id):
        """
            更新 PC 设置的状态、名称和地址
        """

        sqlgo = f"""
                        UPDATE pro_pc_settings 
                        SET `name` = '{name}', `address` = '{address}', `platform` = '{platform}', `state` = {state}, `group` = '{group}', `account` = '{account}', `password` = '{password}', `remark` = {remark}
                        WHERE `id` = {id};
                    """
        # 执行 SQL 更新查询
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data


    def pcSettings_update_state_sql(self, name, state):
        """
            更新 PC 设置的状态、名称和地址
        """

        sqlgo = f"""
                        UPDATE pro_pc_settings 
                        SET  `state` = {state}
                        WHERE `name` = '{name}' and `state` != 2;
                    """
        # 执行 SQL 更新查询
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data

    def pcSettings_select_sql(self, platform=None, state=None):
        """
            @Datetime ： 2024/5/7 10:59
            @Author ：eblis
            @Motto：查询 PC 设置
        """
        # print(platform, state)

        # 根据参数构建 SQL 查询的条件列表
        conditions = []

        # 如果传入了 platform 参数，则添加对应的条件
        if platform:
            conditions.append(f"`platform` = '{platform}'")

        # 如果 state 不为 None，则添加 state 条件
        if state is not None:
            # 如果 state == 3，添加 `state != 2` 条件
            if state == 3:
                conditions.append("`state` != 2")
            else:
                # 如果 state 不是 3，直接添加 `state = {state}` 条件
                conditions.append(f"`state` = {state}")

        # 构建最终的 SQL 查询
        if conditions:
            sqlgo = f"SELECT /*+ NOCACHE */ * FROM pro_pc_settings WHERE {' AND '.join(conditions)} ORDER BY state;"
        else:
            # 如果没有其他条件，默认查询所有记录
            sqlgo = "SELECT /*+ NOCACHE */ * FROM pro_pc_settings ORDER BY state;"

        # print("sqlgo:", sqlgo)
        sql_data = self.ssql.mysql_select('basis', sqlgo)
        return sql_data


    ############################################# blogger #####################################################


    def blogger_info_list_sql(self):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""SELECT /*+ NOCACHE */*  FROM seo_blogger_info ORDER BY create_at DESC;"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_select('basis', sqlgo)
        return sql_data


    def blogger_info_insert_sql(self, group,adsNumber, adsID, proxy, bloggerID, create_at):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""INSERT INTO seo_blogger_info (`group`,`adsNumber`,`adsID`, `proxy`, `bloggerID`, `create_at`) VALUES ('{group}','{adsNumber}','{adsID}','{proxy}','{bloggerID}', '{create_at}');"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data


    def blogger_info_delete_sql(self, id):
        # noinspection SqlNoDataSourceInspection
        sqlgo = f"""DELETE FROM seo_blogger_info WHERE `id` = '{id}';"""
        # 执行 SQL 查询语句
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data

    def blogger_info_update_sql(self, group, adsNumber, adsID, proxy, bloggerID, id):
        """
            更新 PC 设置的状态、名称和地址
        """

        sqlgo = f"""
                        UPDATE seo_blogger_info 
                        SET `group` = '{group}', `adsNumber` = '{adsNumber}', `adsID` = '{adsID}', `proxy` = '{proxy}', `bloggerID` = '{bloggerID}'
                        WHERE `id` = {id};
                    """
        # 执行 SQL 更新查询
        sql_data = self.ssql.mysql_commit('basis', sqlgo)
        return sql_data


    def blogger_info_select_sql(self, group=None):
        """
            @Datetime ： 2024/5/7 10:59
            @Author ：eblis
            @Motto：查询 PC 设置
        """
        # print("pcSettings_select, locals():", locals())

        # 构建参数字典，过滤掉 None 和空字符串
        params = {k: v for k, v in locals().items() if k in ['group'] and v not in [None, ""]}
        print("非 None 的参数名：", list(params.keys()))

        # 根据参数构建 SQL 查询
        if params:
            conditions = [f"`{k}` = '{v}'" for k, v in params.items()]
            sqlgo = f"SELECT /*+ NOCACHE */ * FROM seo_blogger_info WHERE {' AND '.join(conditions)} ORDER BY create_at DESC;"
        else:
            sqlgo = "SELECT /*+ NOCACHE */ * FROM seo_blogger_info ORDER BY create_at DESC;"

        # print("生成的 SQL 查询:", sqlgo)

        # 执行查询
        sql_data = self.ssql.mysql_select('basis', sqlgo)
        return sql_data

