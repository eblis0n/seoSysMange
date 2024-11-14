# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/24 01:19
@Author ： eblis
@File ：article_sql_go.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import subprocess

from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
import middleware.public.configurationCall as configCall
from backendServices.src.awsMQ.amazonSQS import AmazonSQS

class getCookie():
    def __init__(self):
        self.usego = otherUse()
        self.ssql = basis_sqlGO()
        self.aws_sqs = AmazonSQS()

    def run(self, pcname, queue_url, adsIDlist):
        """
            @Datetime ： 2024/8/27 13:33
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"{queue_url} 执行")
        response_cookie = []
        for adsID in adsIDlist:
            self.get_cookie(adsID, response_cookie)
        print("get_cookie执行完了，可以下一步")
        # time.sleep(3)
        for cookiedata in response_cookie:
            cookiedict = self.usego.changeDict(cookiedata)
            print("cookiedict", cookiedict)
            sql_data = self.ssql.note_users_info_update_cookie(cookie=cookiedict["cookie"], adsID=cookiedict["user_id"])
            self.ssql.pcSettings_update_state_sql(pcname, state=0)
            self.aws_sqs.deleteMSG(queue_url)
            if "sql 语句异常" not in str(sql_data):

                print(f'{cookiedict["user_id"]},入库成功！！！')
                return True
            else:
                print(f'{cookiedict["user_id"]}入库失败')
                return False



    def get_cookie(self, adsID, response_cookie):
        """
            @Datetime ： 2024/8/27 00:04
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"来把～ {adsID},开始获取cookie")

        result = subprocess.run(
            [
                "node",  # Node.js 命令
                configCall.note_get_cookie_js,  # Node.js 脚本路径
                configCall.adsServer,  # adsServer 参数
                adsID # adsID 参数
                # filepath  # filepath 参数
            ],
            capture_output=True,  # 捕获输出
            text=True  # 以文本格式处理输出
        )

        # 打印 Node.js 脚本的标准输出
        print(f"Node.js 脚本的标准输出:{result.stdout}")

        response_cookie.append(result.stdout)

        # 打印 Node.js 脚本的标准错误
        # if result.stderr:
        #     print("Node.js 脚本的标准错误:")
        #     print(result.stderr)

        # 检查 Node.js 脚本是否执行成功
        if result.returncode == 0:
            print("Node.js 脚本执行成功")
        else:
            print(f"Node.js 脚本执行失败，错误码: {result.returncode}")






if __name__ == '__main__':
    getGO = getCookie()
    adsIDlist = ["klak6h9"]
    getGO.run(adsIDlist)
