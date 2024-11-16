# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/23 16:00
@Author ： eblis
@File ：google_online_insert.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
import publicFunctions.configuration as config
from publicFunctions.commonUse import commonUse
from googleapiclient.discovery import build
from google.oauth2 import service_account

class googleOnlineInsert():
    def __init__(self):
        self.comm = commonUse()

        # self.jiao_sql = jiao_sqlCollectionGO()
        self.credentials = service_account.Credentials.from_service_account_file(config.service_account_file,
                                                                                 scopes=[
                                                                                     'https://www.googleapis.com/auth/spreadsheets',
                                                                                     'https://www.googleapis.com/auth/drive'])

    def google_online_create(self, title, sheet_title):
        """
            @Datetime ： 2024/9/19 15:11
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 创建一个新的 Google Sheets 文件
        spreadsheet = {
            'properties': {
                'title': title
            },
            'sheets': [
                {
                    'properties': {
                        'title': sheet_title
                    }
                }
            ]
        }
        # 创建服务对象
        service = build('sheets', 'v4', credentials=self.credentials)
        spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()

        # 获取新电子表格的 ID
        spreadsheet_id = spreadsheet.get('spreadsheetId')

        return spreadsheet_id



    def google_online_batch(self, spreadsheet_id, SERVICE_ACCOUNT_EMAIL, MAIN_ACCOUNT_EMAIL, ):
        """
            @Datetime ： 2024/9/19 15:52
            @Author ：eblis
            @Motto：创建一个新的 batch HTTP 请求
        """
        # 创建 Drive 服务对象
        drive_service = build('drive', 'v3', credentials=self.credentials)
        batch = drive_service.new_batch_http_request(callback=self.callback)

        # 将新电子表格共享给服务帐号
        service_account_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': SERVICE_ACCOUNT_EMAIL
        }
        batch.add(drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=service_account_permission,
            fields='id',
        ))

        # 将新电子表格共享给主帐号
        main_account_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': MAIN_ACCOUNT_EMAIL
        }
        batch.add(drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=main_account_permission,
            fields='id',
        ))

        # 执行 batch 请求
        batch.execute()

    # 定义回调函数来处理 batch 请求的结果
    def callback(self, request_id, response, exception):
        if exception:
            # Handle error
            print(exception)
        else:
            print(f"Permission Id: {response.get('id')}")