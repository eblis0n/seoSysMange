# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/3 20:48
@Author ： eblis
@File ：spidergo.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import requests
import publicFunctions.configuration as config
import datetime

class ahrefsAPI():

    def query_ahrefs_api(self, base_url, domain, api_token):
        # 获取今天的日期
        today = datetime.datetime.now()

        # 格式化日期
        formatted_date = today.strftime("%Y-%m-%d")
        print(f"当前日期：{formatted_date}")
        params = {
            "date": f'{formatted_date}',
            "target": domain,
        }
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        # print("base_url",base_url)
        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get("metrics", {})
            return {
                "domain": domain,
                "organic_keywords": metrics.get("org_keywords"),
                "organic_traffic": metrics.get("org_traffic")
            }
        else:
            print(f"查询 {domain} 失败,状态码: {response.status_code}")
            return None


if __name__ == "__main__":
    ahrefs = ahrefsAPI()

    domain = "haitoukins.com"

    print(ahrefs.query_ahrefs_api(config.ahrefs_base_url, domain, config.ahrefs_api_token))