# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/3 20:22
@Author ： eblis
@File ：spiderGO.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import time

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/3 20:48
@Author ： eblis
@File ：spidergo.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import os
import sys
from datetime import datetime
import json
import requests

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from publicFunctions.commonUse import commonUse
import publicFunctions.configuration as config


class spidergo():
    def __init__(self):
        self.comm = commonUse()
        # self.jiao_sql = jiao_sqlCollectionGO()

    def run_keywords(self, keywords, domain):
        """
            @Datetime ： 2024/9/3 23:09
            @Author ：eblis
            @Motto：简单描述用途
        """
        current_at = datetime.now().strftime("%Y%m%d")
        folder_path = config.google_file

        domain_path = self.domain_log(domain, folder_path, current_at)

        domain_file, yes, no = self.search_keywords(keywords, domain_path)
        return domain_file, yes, no

    def run_ip(self, domain):
        """
            @Datetime ： 2024/9/3 23:09
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"{domain}准备查蜘蛛")
        current_at = datetime.now().strftime("%Y%m%d")
        folder_path = config.google_file

        if self.check_file(current_at, folder_path):
            print("存在包含当前日期的文件。")
        else:
            print("不存在包含当前日期的文件。")
            self.get_developers(current_at, folder_path)


        with open(f"{folder_path}/googlebot_{current_at}.txt", 'r', encoding='utf-8') as f:
            googlebot_data = f.read()

        googlebot_dict = self.comm.changeDict(googlebot_data)

        domain_path = self.domain_log(domain, folder_path, current_at)
        domain_file, yes, no = self.calibration(googlebot_dict, domain_path)

        return domain_file, yes, no


    def check_file(self, current_at,directory):
        # current_at = datetime.datetime.now().strftime("%Y%m%d")
        # directory = '/path/to/your/directory'  # 替换为你需要检查的文件夹路径
        for filename in os.listdir(directory):
            if "googlebot" in filename:
                if current_at in filename:
                    return True
        return False



    def domain_log(self, domain, folder_path, current_at):
        """
            @Datetime ： 2024/9/3 22:51
            @Author ：eblis
            @Motto：将 目标域名log 保存成文件
        """
        # file_name = domain.replace('https://', "").replace(".com", "")
        print(f"{domain} 准备蜘蛛")
        # domain_name = domain.split('https://')[1]
        # print("domain_name",domain_name,domain)
        this_file_path = f"{folder_path}/{domain}_{current_at}.txt"
        # print("file_name",this_file_path)

        log = f"https://{domain}/caddy-logs/{domain}.log"
        try:
            this1 = requests.get(log)
        except:
            print("出现了异常，稍等重试")
            time.sleep(2)
            this1 = requests.get(log)

        domain_log_data = this1.text
        with open(this_file_path, "w+", encoding='utf-8') as f:
            f.write(domain_log_data)
        return this_file_path

    
    def search_keywords(self, keywords, domain_file):
        """
            @Datetime ： 2024/9/20 17:22
            @Author ：eblis
            @Motto：简单描述用途
        """
        yes = 0
        no = 0
        with open(domain_file, 'r', encoding='utf-8') as f:
            log_data = f.readlines()

        for logdd in log_data:
            log_dict = self.comm.changeDict(logdd)
            headers = log_dict['request']['headers']

            try:
                # 将字典转换为字符串
                headers_str = json.dumps(headers)
                # print("headers", headers_str)
                if any(keyword in headers_str for keyword in keywords):
                    yes = yes + 1
                else:
                    no = no + 1
            except:
                # print("没有找到元素")
                print("headers，没有找到元素", headers)
                no = no + 1

        return domain_file, yes, no


    def get_developers(self, current_at, file_path):
        """
            @Datetime ： 2024/9/3 23:06
            @Author ：eblis
            @Motto：简单描述用途
        """

        this_file_path = f"{file_path}/googlebot_{current_at}.txt"
        googlebot = "https://developers.google.com/search/apis/ipranges/googlebot.json"
        googlebot1 = requests.get(googlebot)
        with open(this_file_path, "w+", encoding='utf-8') as f:
            f.write(googlebot1.text)
        return this_file_path

    def calibration(self, googlebot_dict, domain_file):
        """
            @Datetime ： 2024/9/3 23:13
            @Author ：eblis
            @Motto：简单描述用途
        """
        yes = 0
        no = 0
        prefixes = []
        with open(domain_file, 'r', encoding='utf-8') as f:
            log_data = f.readlines()

        # print(googlebot_dict['prefixes'])
        for googlebot2 in googlebot_dict['prefixes']:
            #     # print(type(googlebot2),googlebot2)
            for k, v in googlebot2.items():
                prefixes.append(v.split('/')[0])


        for i in range(len(log_data)):
            thisStep = json.loads(log_data[i])
            headers = thisStep['request']['headers']
            headers_dict = self.comm.changeDict(headers)
            try:

                connectingIp = headers_dict['Cf-Connecting-Ip'][0]
                if ":" in connectingIp:
                    thisIP = ":".join(connectingIp.split(":")[:4])
                else:
                    thisIP = connectingIp
                # print("thisIP", thisIP)
                if thisIP in prefixes:
                    # print("yes")
                    yes = yes + 1
                else:
                    # print("no")
                    no = no + 1
            except:
                print("headers，没有找到元素", headers)
                no = no + 1

        return domain_file, yes, no

if __name__ == '__main__':
    # comm = commonUse()
    spi = spidergo()

    domain = "monetaryinvest.com"

    # with open(f"/Users/eblis/project/shanQ/ProFilePro/ProFileSys/docsFile/wp_some/googlebot_20240920.txt", 'r', encoding='utf-8') as f:
    #     googlebot_data = f.read()
    # #
    # googlebot_dict = spi.comm.changeDict(googlebot_data)
    # domain_file = '/Users/eblis/project/shanQ/ProFilePro/ProFileSys/docsFile/wp_some/kabunokaidoki.com_20240920.txt'
    # keywords = ["Googlebot", 'googlebot(at)googlebot.com']
    domain_file, yes, no = spi.run_ip(domain)
    print(domain_file, yes, no)

    # print(spi.run_keywords(keywords, domain))
    # print(spi.calibration(googlebot_dict, domain_file))
    # print(spi.search_keywords(keywords, domain_file))
