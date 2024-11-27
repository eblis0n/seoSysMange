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
from concurrent.futures import ThreadPoolExecutor
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

        # response_cookie = []  # 用于存储获取到的 cookie
        batch_size = 10  # 每个批次处理 10 个 adsID

        # 用于存储每个批次的失败数据
        failed_data = []

        # 线程池处理每个批次的函数
        def process_ads_batch(batch_adsID):
            batch_response_cookie = []
            for adsID in batch_adsID:
                jsresponse = self.get_cookie(adsID)
                print(f"get_cookie 输出的结果：{jsresponse}")
                if jsresponse is not None:
                    batch_response_cookie.append(jsresponse)
            print(f"：这批次获取到的cookie结果{batch_response_cookie}")

            # 每个批次完成后将数据插入数据库，并将入库失败的数据记录
            batch_failed_data = []
            for cookiedata in batch_response_cookie:
                cookiedict = self.usego.changeDict(cookiedata)
                print(f'cookiedict：{cookiedict}')

                try:
                    sql_data = self.ssql.note_users_info_update_cookie(useragent=cookiedict["user-agent"], cookie=cookiedict["cookie"],
                                                                       adsID=cookiedict["user_id"])
                    if "sql 语句异常" in str(sql_data):
                        batch_failed_data.append(cookiedict)  # 失败的数据保留
                    else:
                        print(f'{cookiedict["user_id"]},入库成功！！！')
                except Exception as e:
                    print(f" 出现异常了: {e}")
                    batch_failed_data.append(cookiedict)  # 失败的数据保留

            # 将每个批次失败的数据保留到 `failed_data`
            failed_data.extend(batch_failed_data)

        # 将 adsIDlist 分割成多个批次
        batches = [adsIDlist[i:i + batch_size] for i in range(0, len(adsIDlist), batch_size)]

        # 使用 ThreadPoolExecutor 执行每个批次
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            executor.map(process_ads_batch, batches)


        # 如果有失败的数据（数据库插入失败的记录），返回失败
        if failed_data:
            print(f"以下数据入库失败：{failed_data}")
            for cookiedata in failed_data:
                cookiedict = self.usego.changeDict(cookiedata)
                try:
                    sql_data = self.ssql.note_users_info_update_cookie(useragent=cookiedict["useragent"], cookie=cookiedict["cookie"],
                                                                       adsID=cookiedict["user_id"])
                    if "sql 语句异常" in str(sql_data):
                        print(f"没救了，二次入库失败{cookiedict}")
                    else:
                        print(f'{cookiedict["user_id"]},入库成功！！！')
                except Exception as e:
                    print(f"没救了，二次入库失败{cookiedict}")

        print("所有批次的 get_cookie 执行完毕，可以执行后续操作")

        # 处理完成所有批次后的操作：更新状态和删除队列消息
        self.ssql.pcSettings_update_state_sql(pcname, state=0)
        self.aws_sqs.deleteMSG(queue_url)
        return True


    def get_cookie(self, adsID):
        """
            @Datetime ： 2024/8/27 00:04
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"来把～ {adsID},开始获取cookie")
        print(f"js地址：{configCall.note_get_cookie_js}")
        print(f"adsServer:{configCall.adsServer}")

        result = subprocess.run(["node", f"{configCall.note_get_cookie_js}",  configCall.adsServer, adsID], capture_output=True, text=True)


        # 打印 Node.js 脚本的标准输出
        print(f"Node.js 脚本的标准输出:{result.stdout}")


        # 打印 Node.js 脚本的标准错误
        if result.stderr:
            print("Node.js 脚本的标准错误:")
            print(result.stderr)

        # 检查 Node.js 脚本是否执行成功
        if result.returncode == 0:
            print("Node.js 脚本执行成功")
            return result.stdout
        else:
            print(f"Node.js 脚本执行失败，错误码: {result.returncode}")
            return None






if __name__ == '__main__':
    getGO = getCookie()
    adsIDlist = ["klak6mp"]
    queue_url = "/"
    getGO.run(configCall.client_id, queue_url, adsIDlist)
