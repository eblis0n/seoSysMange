# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 21:36
@Author ： eblis
@File ：spliceGo.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
import middleware.public.configurationCall as configCall
class spliceGo():
    def __init__(self):
        self.usego = otherUse()
        self.mossql = mongo_sqlGO()

    def splice_301(self, files):
        if len(files) < 2:
            print("至少需要两个文件")
            return False

        # 读取两个文件内容并生成组合链接
        file_1_path = f"{configCall.temp_file_path}/{files[0]}"
        file_2_path = f"{configCall.temp_file_path}/{files[1]}"

        # 使用生成器来处理大文件，避免内存占用
        with open(file_1_path, 'r', encoding='utf-8') as f1, open(file_2_path, 'r', encoding='utf-8') as f2:
            one_file_links = (line.strip() for line in f1 if line.strip())
            two_file_links = list(line.strip() for line in f2 if line.strip())  # 需要将第二个文件的内容存储为列表

        # 使用生成器表达式避免一次性占用大量内存
        new_links_list = (f"{zy_link}{url}" for zy_link in one_file_links for url in two_file_links)

        # 批量插入生成的链接
        self.mossql.telegra_interim_insert_batch("seo_external_links_post", list(new_links_list))

        return f"生成 {len(list(new_links_list))} 个新链接，已入库"











    
