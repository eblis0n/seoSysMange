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

from backstage.src.googleOnline.google_online_excel_public import googleOnlinePublic
import publicFunctions.configuration as config
from publicFunctions.commonUse import commonUse
from backstage.src.statistics.ahrefs_api import ahrefsAPI


class googleOnlineAhrefs():

    def __init__(self):
        self.comm = commonUse()
        self.public = googleOnlinePublic()
        self.ahrefs = ahrefsAPI()




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
        print("sheet", sheet)

        self.les_go(sheet, groupName)
        print("所有都执行完了")



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
                    result = self.ahrefs.query_ahrefs_api(config.ahrefs_base_url, new_bad_domain[i]["domain"],
                                                          config.ahrefs_api_token)  # 获取域名的 log 数据
                    print(f"重试{i}结果:{result}")
                except Exception as e:
                    print(f"出现异常，跳过: {e}")
                    continue

                else:
                    if result is None:

                        continue
                    else:

                        updates.append({
                            'range': f'{new_bad_domain["keywords"]}',
                            'values': [[result['organic_keywords']]]
                        })
                        updates.append({
                            'range': f'{new_bad_domain["traffic"]}',
                            'values': [[result['organic_traffic']]]
                        })
                        new_bad_domain.remove(new_bad_domain[i])
            nn = nn + 1

        print(f"重试次数耗尽,还有{len(new_bad_domain)} 无力回天：{new_bad_domain} 自己想办法吧")


    def les_go(self, sheet, groupName):
        """
            @Datetime ： 2024/9/20 01:30
            @Author ：eblis
            @Motto：遍历指定表格并处理数据
        """

        # 获取当前日期
        today = self.public.weekday()


        # 如果是星期一，清理旧文件和数据
        if today == "星期一":
            print("今天是星期一")
            self.public.del_old_file()  # 删除旧文件
            self.public.del_old_data(sheet)  # 删除旧数据

        # 查找当前日期所在的列
        cell = sheet.find(today)
        if not cell:
            print(f"未找到列 {today}")
            return

        print("cell", cell)

        # 获取表格的所有行
        rows = sheet.get_all_values()
        keywords_column, traffic_column = self.public.get_today_columns()

        # 批量更新的数据缓存
        updates = []

        bad_domain = []
        domain_data = {
            'domain': '',
            'keywords': '',
            'traffic': ''

        }

        for i, row in enumerate(rows, start=1):
            # 跳过前两行（假设它们是表头）
            if i < 4:
                continue

            # 跳过空行
            if not any(row):
                continue

            # 跳过 groupName 中的域名
            if row[0] in groupName:
                continue


            # print("Row content:", row)
            cleaned_domain = row[0].rstrip()
            # print("cleaned_domain",cleaned_domain)
            print(f"Row number: {i},{cleaned_domain}")
            try:
                result = self.ahrefs.query_ahrefs_api(config.ahrefs_base_url,  cleaned_domain, config.ahrefs_api_token) # 获取域名的 log 数据
            except Exception as e:
                print(f"处理域名 {cleaned_domain} 时出现异常，跳过。错误信息: {str(e)}")
                domain_data['keywords'] = f'{keywords_column}{i}'
                domain_data['traffic'] = f'{traffic_column}{i}'
                domain_data['domain'] = cleaned_domain
                bad_domain.append(domain_data)
                continue
            else:
                # print("result", result)
                if result is None:
                    print("None了")
                    domain_data['keywords'] = f'{keywords_column}{i}'
                    domain_data['traffic'] = f'{traffic_column}{i}'
                    domain_data['domain'] = cleaned_domain
                    bad_domain.append(domain_data)
                    continue
                else:
                    updates.append({
                        'range': f'{keywords_column}{i}',
                        'values': [[result['organic_keywords']]]
                    })
                    updates.append({
                        'range': f'{traffic_column}{i}',
                        'values': [[result['organic_traffic']]]
                    })

        if int(config.site_retry) > 0 and bad_domain != []:
            self.retry(int(config.site_retry), bad_domain, updates)

        print(f"跑完了，待更新数据:{updates}")
        # 批量更新所有需要更新的单元格
        if updates:
            self.public.update_date(sheet, updates)
        else:
            print("没有需要更新的数据")


if __name__ == '__main__':
   excel = googleOnlineAhrefs()
   excel.run_vertical(config.google_docs_url, config.sheetTab_ahrefs, eval(config.sheetGroupName))

