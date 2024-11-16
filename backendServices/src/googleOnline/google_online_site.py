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

from gspread.utils import rowcol_to_a1
import publicFunctions.configuration as config
from publicFunctions.commonUse import commonUse
from backstage.src.statistics.siteGO import sitego
from backstage.src.googleOnline.google_online_excel_public import googleOnlinePublic


class googleOnlineSite():
    def __init__(self):
        self.comm = commonUse()
        self.public = googleOnlinePublic()
        self.site = sitego()

    def run_vertical(self, target_url, sheetTab, groupName):
        """
            @Datetime ： 2024/9/20 01:02
            @Author ：eblis
            @Motto：遍历指定表格
        """

        workbook = self.public.google_online_excel_workbook(target_url)
        # sheets = workbook.worksheets
        # print("sheets",sheets)

        sheet = workbook.worksheet(sheetTab)
        # print("sheet", sheet)

        self.les_go(sheet, groupName)
        print("所有都执行完了")

    def run_Horizontal(self, target_url, groupName):
        """
            @Datetime ： 2024/9/20 01:23
            @Author ：eblis
            @Motto：遍历所有表格
        """
        workbook = self.public.google_online_excel_workbook(target_url)
        # 获取所有的工作表
        all_sheets = workbook.worksheets()

        # 遍历所有的工作表
        for sheet in all_sheets:
            # 你可以在这里对每个工作表进行操作
            print("Working with sheet:", sheet.title)
            sheet = workbook.worksheet(sheet.title)
            self.les_go(sheet, groupName)

        print("所有都执行完了")

    def les_go(self, sheet, groupName):
        """
        @Datetime ： 2024/9/20 01:30
        @Author ：eblis
        @Motto：简单描述用途
        """
        today = self.public.weekday()
        print(f"今天是{today}")
        if today == "星期一":
            self.public.del_old_data(sheet)

        cell = sheet.find(today)
        print("cell", cell)

        rows = sheet.get_all_values()
        updates = []  # 创建一个列表来存储批量更新
        bad_domain = []
        domain_data = {
            'rowcol': '',
            'domain': ''
        }

        for i, row in enumerate(rows, start=1):
            if i < 3:
                continue
            if not any(row):  # Skip the row if it's empty
                continue

            if row[0] in groupName:
                # print(f"{row[0]}")
                continue
            print("Row number:", i)
            print("Row content:", row)
            print("Cell content:", cell.col)
            cleaned_domain = row[0].rstrip()

            try:
                result = self.site.run(cleaned_domain)
            except Exception as e:
                print(f"出现异常，跳过: {e}")
                domain_data['rowcol'] = f'{rowcol_to_a1(i, cell.col)}'
                domain_data['domain'] = cleaned_domain
                bad_domain.append(domain_data)
                continue
            else:
                if result is None:
                    domain_data['rowcol'] = f'{rowcol_to_a1(i, cell.col)}'
                    domain_data['domain'] = cleaned_domain
                    bad_domain.append(domain_data)
                    continue
                else:
                    try:
                        val = int(result)
                    except:
                        val = result
                    updates.append({
                        'range': f'{rowcol_to_a1(i, cell.col)}',  # 要更新的单元格范围
                        'values': [[val]]  # logdata 的第一个值
                    })
        if int(config.site_retry) > 0 and bad_domain != []:
            self.retry(int(config.site_retry), bad_domain, updates)

        print(f"跑完了，待更新数据:{updates}")

        if updates:
            self.public.update_date(sheet, updates)
        else:
            print("没有需要更新的数据")

    def retry(self, num, bad_domain, updates):
        """
            @Datetime ： 2024/10/14 19:38
            @Author ：eblis
            @Motto：简单描述用途
        """
        nn = 0
        new_bad_domain = bad_domain
        while nn < num and len(new_bad_domain) > 0:
            print(f"第 {nn} 次 重试，{new_bad_domain}")
            for i in range(len(new_bad_domain)):
                try:
                    result = self.site.run(new_bad_domain[i]['domain'])

                except Exception as e:
                    print(f"出现异常，跳过: {e}")
                    continue
                else:
                    if result is None:
                        continue
                    else:
                        try:
                            val = int(result)
                        except:
                            val = result
                        updates.append({
                            'range': new_bad_domain[i]['rowcol'],  # 要更新的单元格范围
                            'values': [[val]]
                        })
                        new_bad_domain.remove(new_bad_domain[i])
            nn = nn + 1

        print(f"重试次数耗尽,还有{len(new_bad_domain)},{new_bad_domain} 自己想办法吧")




if __name__ == '__main__':
   excel = googleOnlineSite()
   excel.run_vertical(config.google_docs_url, config.sheetTab_site, eval(config.sheetGroupName))
