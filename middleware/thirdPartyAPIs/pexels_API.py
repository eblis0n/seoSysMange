# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/12/12 22:41
@Author ： eblis
@File ：pexels_API.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import random
import sys


base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
import requests

class pexelsAPI():

    def pexelsGO(self, pexelsKEY, nature):
        """
            @Datetime ： 2024/12/12 22:42
            @Author ：eblis
            @Motto：简单描述用途
        """

        # 设置 API 地址和认证信息
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": f"{pexelsKEY}"  # 替换为你的 Pexels API 密钥
        }
        params = {
            "query": f"{nature}",  # 查询关键字
            "per_page": 10  # 每页返回的图片数量
        }

        # 发送 GET 请求
        response = requests.get(url, headers=headers, params=params)

        # 检查请求是否成功
        if response.status_code == 200:
            data = response.json()  # 将响应内容解析为 JSON
            photos = random.choice(data["photos"])
            # print("photos",photos)
            this_photos = photos['src']['original']
            # print(response.json())  # 打印失败的详细信息
            this_atap = f"""<a href="https://www.pexels.com"><img src="{this_photos}" /></a>"""
            return this_atap
        print(f"请求失败或未找到图片，状态码: {response.status_code}")
        return None

if __name__ == '__main__':
    pp = pexelsAPI()
    pexelsKEY = "Jns8OtyLkzpHS8OcCIphfCGBpj2DDh5cHwySqTiWV9zgA0VZobfQmbQz"
    nature = "金融"
    print(pp.pexelsGO(pexelsKEY, nature))