# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/6/13 11:50
@Author ： eblis
@File ：upload_file_manage.py
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
from middleware.public.commonUse import otherUse
# from middleware.public.readExcel import excelGO
from backendServices.src.assistance.spliceGo import spliceGo

import middleware.public.configurationCall as configCall


class uploadFileManage():
    def __init__(self):
        self.bp = Blueprint("uploadFile", __name__, url_prefix="/upload")

        self.Myenum = MyEnum()
        self.usego = otherUse()

        # 将路由和视图函数绑定到蓝图
        self.bp.route(self.Myenum.UPLOAD_FILE, methods=['POST'])(self.upload_files)

    def upload_files(self):
        """
            @Datetime ： 2024/7/2 00:18
            @Author ：eblis
            @Motto：上传多份文件
        """
        data_request = request.form
        who = data_request.get('who')
        files = request.files.getlist('file')  # 获取所有上传的文件

        # 判断是否上传了文件
        if not files:
            self.usego.sendlog('未接收到任何文件')
            return ResMsg(code=400, msg='未接收到任何文件').to_json()

        valid_extensions = ('xls', 'xlsx', 'csv', 'txt')  # 支持的文件格式
        file_name = []

        # 遍历并处理每个文件
        for file in files:
            # 检查文件后缀是否合法
            if file.filename.endswith(valid_extensions):
                # 保存文件
                file.save(os.path.join(configCall.temp_file_path, file.filename))
                file_name.append(file.filename)
                print(f"接收到文件：{file.filename}，属于 {who} 类型")

            else:
                self.usego.sendlog(f'文件 {file.filename} 超出接收范围')
                return ResMsg(code=400, msg=f'文件 {file.filename} 超出接收范围，只接收 xls, xlsx, csv, txt 格式').to_json()

        # 根据 `who` 参数执行不同逻辑
        if who == "email" or who == "oauth":
            print(f"接收到 {who} 批量：{file_name}")
            res = ResMsg()

        elif who == "file301":
            if len(file_name) == 2:
                spl = spliceGo()
                spl.splice_301(file_name)
                res = ResMsg()
            else:
                return ResMsg(code=400, msg=f'file301 请求需要 2 个文件').to_json()

        else:
            self.usego.sendlog(f'无法识别 {who} 请求')
            return ResMsg(code=400, msg=f'无法识别 {who} 请求').to_json()

        return res.to_json()

    # def upload_file(self):
    #     """
    #         @Datetime ： 2024/7/2 00:18
    #         @Author ：eblis
    #         @Motto：简单描述用途
    #     """
    #
    #     data_request = request.form
    #     who = data_request['who']
    #     file = request.files['file']
    #     create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    #     # 如果是xls、xlsx或csv文件，则读取内容并上传到数据库
    #     if file.filename.endswith(('xls', 'xlsx', 'csv')):
    #         # exc = excelGO()
    #         # 保存上传的文件到指定路径
    #         if who == "email":
    #             file.save(os.path.join(configCall.temp_file_path, file.filename))
    #             print("接收到一份email批量")
    #             # df = exc.pd_read_table_info(configCall.temp_file_path, file.filename)
    #             # df1 = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    #             #
    #             # batch = []
    #             #
    #             # for index, row in df1.dropna(axis=1, how='all').drop_duplicates().iterrows():
    #             #     row_list = list(row)
    #             #     row_list.append(create_at)
    #             #     row_tuple = tuple(row_list)
    #             #     batch.append(row_tuple)
    #
    #             # sql_data = self.ssql.email_insert_excle(batch)
    #             # if "sql 语句异常" not in str(sql_data):
    #             #     self.usego.sendlog(f'batch：{batch}')
    #             #     res = ResMsg()
    #             #     responseData = res.to_dict()
    #             # else:
    #             #     self.usego.sendlog(f'导入失败{sql_data}')
    #             #     res = ResMsg(code=400, msg=f'导入失败{sql_data}')
    #             #     responseData = res.to_json()
    #             res = ResMsg()
    #             responseData = res.to_dict()
    #         elif who == "oauth":
    #             file.save(os.path.join(configCall.temp_file_path, file.filename))
    #             print("接收到一份oauth批量")
    #             # df = exc.pd_read_table_info(configCall.temp_file_path, file.filename)
    #             # df1 = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
    #             #
    #             # batch = []
    #             #
    #             # for index, row in df1.dropna(axis=1, how='all').drop_duplicates().iterrows():
    #             #     row_list = list(row)
    #             #     row_list.append(create_at)
    #             #     row_tuple = tuple(row_list)
    #             #     batch.append(row_tuple)
    #             # print("batch",batch)
    #             #
    #             # sql_data = self.ssql.google_oauth_insert_excle(batch)
    #             #
    #             # if "sql 语句异常" not in str(sql_data):
    #             #     self.usego.sendlog(f'batch：{batch}')
    #             #     res = ResMsg()
    #             #     responseData = res.to_dict()
    #             # else:
    #             #     self.usego.sendlog(f'导入失败{sql_data}')
    #             #     res = ResMsg(code=400, msg=f'导入失败{sql_data}')
    #             #     responseData = res.to_json()
    #             res = ResMsg()
    #             responseData = res.to_dict()
    #         else:
    #             self.usego.sendlog(f'无法识别')
    #             res = ResMsg(code=400, msg=f'无法识别')
    #             responseData = res.to_json()
    #     elif file.filename.endswith(('txt')):
    #         if who == "file301":
    #             file.save(os.path.join(configCall.temp_file_path, file.filename))
    #             print("接收文件成功")
    #
    #
    #
    #             res = ResMsg()
    #             responseData = res.to_dict()
    #         else:
    #             self.usego.sendlog(f'无法识别')
    #             res = ResMsg(code=400, msg=f'无法识别')
    #             responseData = res.to_json()
    #     else:
    #         self.usego.sendlog(f'所上传的文件超出接收范围，只接收 xls, xlsx, csv 格式')
    #         res = ResMsg(code=10001, msg=f'所上传的文件超出接收范围，只接收 xls, xlsx, csv 格式')
    #         responseData = res.to_json()
    #
    #     return responseData





