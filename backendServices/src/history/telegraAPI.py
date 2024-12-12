# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/8/2 14:45
@Author ： eblis
@File ：telegraGO.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import requests
import json

class telegraAPI():
    # def __init__(self):
    #     self.req = RequestUtil()

    def createAccount (self,url,short_name,author_name):
        """
            @Datetime ： 2024/8/2 14:45
            @Author ：eblis
            @Motto：简单描述用途
        """
        data = {
            "short_name": short_name,
            "author_name": author_name
        }

        # 发出 POST 请求
        response = requests.post(url, data=data)
        return response.json()


    def  createPage(self,url,access_token,title,content):
        """
            @Datetime ： 2024/8/2 15:53
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 将内容转换成 JSON 格式
        content_json = json.dumps(content)
        data = {
            "access_token": access_token,
            "title": title,
            "content": content_json,
        }

        response = requests.post(url, data=data)

        # 打印服务器的响应
        return response.json()

if __name__ == '__main__':
    tele = telegraAPI()

    # short_name = "mymy"
    # author_name = "mymy"
    # print(tele.createAccount(url, short_name, author_name))
    url = "https://api.telegra.ph/createPage"

    # 你的 Telegraph 访问令牌
    access_token = "28b708d41cbb5c4a7a9a40bc87d11119ba7a4c28efabd99687ea29dcfd5f"

    # 页面的标题和作者
    title = "My New Page"


    # 页面的内容
    content = [
        {"tag": "span", "children": ["eeeeeeeeeeee"]},
        {"tag": "p", "children": ["This is my first post on Telegraph."]},
    ]
    print(tele.createPage(url, access_token, title, content))

    
