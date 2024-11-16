# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/3 20:48
@Author ： eblis
@File ：spidergo.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import os
import random
import sys
import time
import middleware.public.configurationCall as configCall
import requests

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from lxml import etree
import re
from fake_useragent import UserAgent

class sitego():


    def headers_config(self):
        ua = UserAgent()
        return {
            'User-Agent': ua.chrome,
        }

    def get_new_proxy(self):
        try:
            response = requests.get(configCall.proxy_add)
            time.sleep(1)
            proxy = response.text.strip()

            print(f"这次使用：{proxy}")
            return proxy
        except Exception as e:
            print(f"Error fetching new proxy: {e}")
            return None

    def google_search(self, domain, proxy):

        headers = self.headers_config()
        url = f"https://www.google.com/search?q=site:{domain}"
        print("url", url)
        try:
            # 随机等待时间
            time.sleep(random.randint(10, 30))
            proxies = {'http': proxy, 'https': proxy}

            response = requests.get(url, headers=headers, proxies=proxies)
            print(f'Requesting {domain} with proxy {proxy}: Status Code {response.status_code}')
            if response.status_code == 200:
                # print("response.text",response.text)
                return response.text
            else:
                return None
        except Exception as e:
            print(f'Error while requesting {domain} with proxy {proxy}: {e}')
            return None

    def extract_result_count(self, html):
        if html:
            try:
                tree = etree.HTML(html)
                result = tree.xpath('//div[@id="result-stats"]/text()')
                if result:
                    data = ''.join(re.findall('\d+', result[0]))
                else:
                    data = 0
            except Exception as e:
                print(f'Error parsing HTML: {e}')
                data = 0
        else:
            data = 0
        return data


    def run(self, domain):
        """
            @Datetime ： 2024/9/3 23:09
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"{domain}准备查site")
        proxy = self.get_new_proxy()
        if proxy is None:
            return None
        else:
            html_text = self.google_search(domain, proxy)
            if proxy is None:
                return None
            else:
                count = self.extract_result_count(html_text)
                return count


if __name__ == '__main__':
    site = sitego()

    domain = "monetaryinvest.com"

    print(site.run(domain))