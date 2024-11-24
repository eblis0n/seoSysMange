# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/14 15:04
@Author ： eblis
@File ：google_online_excel_public.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
import gspread
from google.oauth2 import service_account
import middleware.public.configurationCall as configCall

import glob
import datetime

class googleOnlinePublic():
    def __init__(self):

        self.credentials = service_account.Credentials.from_service_account_file(configCall.service_account_file,
                                                                            scopes=[
                                                                                'https://www.googleapis.com/auth/spreadsheets',
                                                                                'https://www.googleapis.com/auth/drive'])

    def google_online_excel_workbook(self, target_url):
        """
            @Datetime ： 2024/9/20 01:16
            @Author ：eblis
            @Motto：简单描述用途
        """
        gc = gspread.authorize(self.credentials)

        workbook = gc.open_by_url(target_url)  # 打开在线excel地址
        # print("workbook",workbook)
        return workbook

    def new_sheet_title(self, target_url, sheetTab, titlename):
        """
            @Datetime ： 2024/9/23 16:09
            @Author ：eblis
            @Motto：简单描述用途
        """
        workbook = self.google_online_excel_workbook(target_url)
        # sheets = workbook.worksheets
        # print("sheets",sheets)

        sheet = workbook.worksheet(sheetTab)
        for i in range(1, len(titlename)):
            sheet.update_cell(1, i, titlename[i])

    def weekday(self):
        """
            @Datetime ： 2024/10/13 19:41
            @Author ：eblis
            @Motto：简单描述用途
        """
        current_date = datetime.datetime.now()
        weekday_number = current_date.weekday()  # 星期一是0，星期日是6
        weekday_dict = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}
        weekday_str = weekday_dict[weekday_number]
        # print(f"今天是{formatted_date}，{weekday_str}")
        return weekday_str


    def get_today_columns(self):
        current_date = datetime.datetime.now()
        weekday_number = current_date.weekday()  # 星期一是0，星期日是6
        # 星期一对应B和C列,星期二对应D和E列,以此类推
        columns = [('B', 'C'), ('D', 'E'), ('F', 'G'), ('H', 'I'), ('J', 'K'), ('L', 'M'), ('N', 'O')]
        return columns[weekday_number]

    def del_old_data(self, sheet):
        """
            @Datetime ： 2024/10/14 13:37
            @Author ：eblis
            @Motto：清理旧数据
        """
        print("开始清理旧数据！！")

        # 获取所有行的数据
        rows = sheet.get_all_values()

        # 确定需要清理的范围，假设从 B 列到 H 列
        updates = []

        for i, row in enumerate(rows, start=1):
            # 跳过前两行（假设它们是表头）
            if i < 3:
                continue

            print("Row number:", i)
            print("Row content:", row)

            # 设置需要清理的单元格范围
            # 这里假设 H 列是表格的最大列（也可以根据实际情况动态设置）
            if len(row) < 20:  # 若行长度小于8，限制范围到当前行的实际列数
                end_col = chr(ord('B') + len(row) - 1)
            else:
                end_col = 'O'

            # 创建更新数据的字典
            updates.append({
                'range': f'B{i}:{end_col}{i}',  # 清理 B 列到 H 列的范围
                'values': [[''] * (ord(end_col) - ord('B') + 1)]  # 创建空值填充
            })

        # 批量更新所有需要清理的单元格
        if updates:
            self.update_date(sheet, updates)
        else:
            print("没有旧数据需要清理")

    def update_date(self, sheet, datas):
        """
            @Datetime ： 2024/10/14 17:17
            @Author ：eblis
            @Motto：简单描述用途
        """

        try:
            sheet.batch_update(datas)  # 批量更新
            print("更新完成")
        except Exception as e:
            print(f"批量更新时出现错误:{str(e)}")


    def del_old_file(self):
        """
            @Datetime ： 2024/10/14 16:04
            @Author ：eblis
            @Motto：简单描述用途
        """

        # 查找该目录下所有的 .txt 文件
        txt_files = glob.glob(configCall.google_file + "/*.txt")
        # 遍历所有的 .txt 文件并删除
        for txt_file in txt_files:
            os.remove(txt_file)
        print("垃圾已清理！！")