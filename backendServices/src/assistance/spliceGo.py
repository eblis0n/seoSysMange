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
from datetime import datetime

class spliceGo():
    def __init__(self):
        self.usego = otherUse()
        self.mossql = mongo_sqlGO()

    def splice_301(self, sort, genre, platform,  urllist, zyurllist=None):
        """
            @Datetime ： 2024/11/3 15:42
            @Author ：eblis
            @Motto：
            @sort:0拼接，1 不拼接；
            @genre：0重定向；1镜像，2留痕
            @platform：投放平台，
        """

        # 获取当前时间
        now = datetime.now()

        # 格式化为年月日时分秒
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        if zyurllist == "" or zyurllist is None:
            new_links_list = [
                {
                    "url": f"{url}".replace('\n', ''),
                    "platform": platform,
                    "genre": genre,
                    "sort": sort,
                    "create_at": formatted_now
                }
                for url in urllist
            ]
        else:
            new_links_list = [
                {
                    "url": f"{zy_link}{url}".replace('\n', ''),
                    "platform": platform,
                    "genre": genre,
                    "sort": sort,
                    "create_at": formatted_now
                }
                for zy_link in zyurllist
                for url in urllist
            ]
        # self.usego.sendlog(f"拼接结果：{new_links_list}")

        # 批量插入生成的链接
        result = self.mossql.splicing_interim_insert_batch("seo_external_links_post", new_links_list)

        if result is not None:  # 修改这里，检查 result 是否为 None
            return f"生成 {len(new_links_list)} 个新链接，已入库"
        else:
            return None


if __name__ == '__main__':
    spl = spliceGo()

    file_zy301 = f"{configCall.temp_file_path}/zy301.txt"
    file_url301 = f"{configCall.temp_file_path}/url301.txt"
    with open(file_zy301, 'r', encoding='utf-8') as f1, open(file_url301, 'r', encoding='utf-8') as f2:
        zy301_file_links = [line.strip() for line in f1 if line.strip()]
        url301_file_links = [line.strip() for line in f2 if line.strip()]
    result = spl.splice_301(zy301_file_links,url301_file_links, "telegra", "0")
    print(result)
