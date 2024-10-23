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

        file_1_path = f"{configCall.temp_file_path}/{files[0]}"
        file_2_path = f"{configCall.temp_file_path}/{files[1]}"

        try:
            with open(file_1_path, 'r', encoding='utf-8') as f1, open(file_2_path, 'r', encoding='utf-8') as f2:
                one_file_links = [line.strip() for line in f1 if line.strip()]
                two_file_links = [line.strip() for line in f2 if line.strip()]

            # 修改这里，将链接转换为字典
            new_links_list = [{"url": f"{zy_link}{url}"} for zy_link in one_file_links for url in two_file_links]
            print("new_links_list", new_links_list)

            # 批量插入生成的链接
            result = self.mossql.telegra_interim_insert_batch("seo_external_links_post", new_links_list)

            if result is not None:  # 修改这里，检查 result 是否为 None
                return f"生成 {len(new_links_list)} 个新链接，已入库"
            else:
                return "数据库插入操作失败"

        except Exception as e:
            print(f"处理文件时出错: {e}")
            return False

if __name__ == '__main__':
    spl = spliceGo()
    file_name = ["url301.txt", "zy301.txt"]
    result = spl.splice_301(file_name)
    print(result)
