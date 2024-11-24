# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/23 15:08
@Author ： eblis
@File ：google_online_spiders.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import middleware.public.configurationCall as configCall
from backendServices.src.googleOnline.google_online_excel_public import googleOnlinePublic
from backendServices.src.statistics.spiderGO import spidergo
from gspread.utils import rowcol_to_a1
class googleOnlineSpiders():

    def __init__(self):
        self.googlePublic = googleOnlinePublic()
        self.spi = spidergo()




    def run_vertical(self, target_url, sheetTab, groupName):
        """
            @Datetime ： 2024/9/20 01:02
            @Author ：eblis
            @Motto：遍历指定表格
        """

        workbook = self.googlePublic.google_online_excel_workbook(target_url)
        # sheets = workbook.worksheets
        # print("sheets",sheets)

        sheet = workbook.worksheet(sheetTab)
        print("sheet", sheet)

        self.les_go(sheet, groupName)
        print("所有都执行完了")



    def run_Horizontal(self, target_url, groupName):
        """
            @Datetime ： 2024/9/20 01:23
            @Author ：eblis
            @Motto：遍历所有表格
        """
        workbook = self.googlePublic.google_online_excel_workbook(target_url)
        # 获取所有的工作表
        all_sheets = workbook.worksheets()

        # 遍历所有的工作表
        for sheet in all_sheets:
            # 你可以在这里对每个工作表进行操作
            print("Working with sheet:", sheet.title)
            sheet = workbook.worksheet(sheet.title)
            self.les_go(sheet, groupName)

        print("所有都执行完了")




    # def les_go(self, sheet, groupName):
    #     """
    #         @Datetime ： 2024/9/20 01:30
    #         @Author ：eblis
    #         @Motto：简单描述用途
    #     """
    #
    #     # 获取当前日期
    #     today = self.googlePublic.weekday()
    #
    #     if today == "星期一":
    #         print("今天是星期一")
    #         self.googlePublic.del_old_file()
    #         self.googlePublic.del_old_data(sheet)
    #
    #
    #     cell = sheet.find(today)
    #     print("cell", cell)
    #     # # 纵向遍历domain数据并统计蜘蛛数据
    #     rows = sheet.get_all_values()
    #     for i, row in enumerate(rows, start=1):
    #         if i < 3:
    #             continue
    #         if not any(row):  # Skip the row if it's empty
    #             continue
    #     #
    #         if row[0] in groupName:
    #             continue
    #         print("Row number:", i)
    #         print("Row content:", row)
    #         print("Cell content:", cell.col)  # 打印找到的单元格内容
    #         try:
    #             cleaned_domain = row[0].rstrip()
    #             logdata = self.spi.run_ip(cleaned_domain)
    #             # logdata = self.spi.run_keywords(eval(config.googlebot_keywords), row[0])
    #         except:
    #             print("出现异常，跳过")
    #             continue
    #         else:
    #             print("logdata", logdata)
    #             # sheet.update_cell(i, len(row), logdata[1])
    #             sheet.update_cell(i, cell.col, logdata[1])

    def les_go(self, sheet, groupName):
        """
            @Datetime ： 2024/9/20 01:30
            @Author ：eblis
            @Motto：遍历指定表格并处理数据
        """
        # 获取当前日期
        today = self.googlePublic.weekday()

        # 如果是星期一，清理旧文件和数据
        if today == "星期一":
            print("今天是星期一")
            self.googlePublic.del_old_file()  # 删除旧文件
            self.googlePublic.del_old_data(sheet)  # 删除旧数据

        # 查找当前日期所在的列
        cell = sheet.find(today)
        if not cell:
            print(f"未找到列 {today}")
            return

        print("cell", cell)

        # 获取表格的所有行
        rows = sheet.get_all_values()

        # 批量更新的数据缓存
        updates = []

        for i, row in enumerate(rows, start=1):
            # 跳过前两行（假设它们是表头）
            if i < 3:
                continue

            # 跳过空行
            if not any(row):
                continue

            # 跳过 groupName 中的域名
            if row[0] in groupName:
                continue

            print(f"Row number: {i}")
            print("Row content:", row)
            cleaned_domain = row[0].rstrip()
            try:
                logdata = self.spi.run_ip(cleaned_domain)  # 获取域名的 log 数据
            except Exception as e:
                print(f"处理域名 {cleaned_domain} 时出现异常，跳过。错误信息: {str(e)}")
                continue
            else:
                print("logdata", logdata)
                # 将更新操作添加到缓存中，避免多次调用 API
                # 使用字母列名而不是数字
                updates.append({
                    'range': f'{rowcol_to_a1(i, cell.col)}',  # 要更新的单元格范围
                    'values': [[logdata[1]]]  # logdata 的第一个值
                })

        print(f"跑完了，待更新数据:{updates}")
        # 批量更新所有需要更新的单元格
        if updates:
            self.googlePublic.update_date(sheet, updates)
        else:
            print("没有需要更新的数据")


if __name__ == '__main__':
   excel = googleOnlineSpiders()
   excel.run_vertical(configCall.google_docs_url, configCall.sheetTab_spiders, eval(configCall.sheetGroupName))
   # excel.run_Horizontal(config.google_docs_url, eval(config.sheetGroupName))
