# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/15 20:18
@Author ： eblis
@File ：notePostText.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

import requests

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


from middleware.deviceManage.adsDevice import adsDevice
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse



class notePostText:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()



    def run(self, cookie, useragent, proxies, title_alt, content):

        # 获取文章内容链接
        bodydata = content
        # print("bodydata",bodydata)
        try:
            body_length = len(bodydata)
        except:
            body_length = self.usego.randomRandint(1000, 3000)

        headers = {'Content-Type': 'application/json',
                   'cookie': f"{cookie}",
                   'referer': 'https://editor.note.com/',
                   'user-agent': f"{useragent}",
                   'x-requested-with': 'XMLHttpRequest'
                   }  # 设置 HTTP 头部为 JSON

        # print(f"当前代理获取结果{proxies}")
        proxy = {"http": f"{proxies}"}

        # 第一步：进入发帖页面
        dd = self.text_notes(headers, proxy)
        try:
            print(f"进入编辑状态请求结果：{dd['data']}")
        except Exception as e:
            print(f"出现了{e}")
        else:
            print("没有异常，les~go~")
            # # 第二步上传顶部图片
            file = self.get_random_image()
            if file:
                imgage = self.post_image(dd['data']['id'], cookie, useragent,  file, proxies)
                print("imgage", imgage)
            # 第三步:确认发送
            print(f"执行第三步")
            get_post = self.post_text_go(dd['data']['id'], headers, proxy, dd['data']['slug'], bodydata, body_length, title_alt)
            try:
                print(f"发布结果：{get_post['data']}")
            except Exception as e:
                print(f"fget_post,{get_post},{e}")
                return False
            else:
                print(f"{get_post['data']['note_url']} 这篇文章发布了")
                return get_post['data']['note_url']

    def post_image(self, id, cookie, useragent, file, proxies):
        """
            @Datetime ： 2024/8/22 13:58
            @Author ：eblis
            @Motto：文章顶图
        """
        # # Node.js 脚本的路径

        js_path = configCall.note_upload_image_js
        print("执行信息", js_path, str(id), cookie, useragent, file, proxies)

        # 构造命令
        command = [
            "node", js_path, str(id), cookie, useragent, file, proxies
        ]

        # 执行 Node.js 脚本
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"Node.js 脚本的标准输出:{result.stdout}")
            if result.stderr:
                print(f"Node.js 脚本的标准错误:{result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Error running Node.js script: {e.stderr}")
            return False
        return True

    def text_notes(self, headers, proxies):
        """
            @Datetime ： 2024/8/20 22:27
            @Author ：eblis
            @Motto：进入编辑页面
        """

        url = "https://note.com/api/v1/text_notes"

        data = {
            "template_key": "null".replace('"', "")  # 在 Python 中，None 对应于 JSON 的 null
        }
        # print("proxies",proxies)


        if proxies is None:

            response = requests.post(url, headers=headers, data=json.dumps(data))
        else:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxies,
                                         timeout=60)
                print("成功使用代理")
            except:
                response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 201:
            return response.json()
        else:
            print(f"{response.status_code}, {response.text}")
            return False


    def post_text_go(self, id, headers, proxies, slug, bodydata, body_length, title):
        """
            @Datetime ： 2024/8/20 22:40
            @Author ：eblis
            @Motto：确认发送并返回url
        """
        print(f"开始")
        url = f"https://note.com/api/v1/text_notes/{id}"
        data = {
            "author_ids": [],
            "body_length": body_length,
            "disable_comment": False,
            "free_body": f'{bodydata}',
            "hashtags": [],
            "image_keys": [],
            "index": True,
            "is_refund": False,
            "limited": False,
            "magazine_ids": [],
            "magazine_keys": [],
            "name": f'{title}',
            "pay_body": "",
            "price": 0,
            "send_notifications_flag": True,
            "separator": "null".replace('"', ""),
            "slug": slug,
            "status": "published",
            "circle_permissions": [],
            "discount_campaigns": [],
            "lead_form": {"is_active": False, "consent_url": ""}
        }

        print(f"传参：{url},{data},{proxies}")

        if proxies is None:
            response = requests.put(url, headers=headers, data=json.dumps(data))
        else:
            try:
                response = requests.put(url, headers=headers, data=json.dumps(data), proxies=proxies,
                                        timeout=60)
                print("成功使用代理")
            except Exception as e:
                # response = requests.put(url, headers=headers, data=json.dumps(data))
                print(f"代理失败原因{e}")
                time.sleep(3)
                print("再尝试一下使用代理")
                try:
                    response = requests.put(url, headers=headers, data=json.dumps(data), proxies=proxies,
                                            timeout=60)
                    print("二次尝试，成功使用代理")
                except Exception as e:
                    print(f"2次代理失败原因{e}")
                    response = requests.put(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:

            return response.json()
        else:
            print(f"{response.status_code}, {response.text}")
            return None



    def get_random_image(self):
        # 获取目录中所有的 .jpg 文件
        directory = f"""{configCall.note_path}/image"""
        jpg_files = [f for f in os.listdir(directory) if f.endswith(('.jpeg', '.jpg', '.png'))]

        if not jpg_files:
            print("没有找到 图片 文件")
            return False

        # 随机选择一个文件
        random_file = self.usego.randomChoice(jpg_files)

        # 返回文件的完整路径
        return f"""{directory}/{random_file}"""




if __name__ == '__main__':
    pass
    # note = notePostText()
    # # 调试，通过配置文件修改
    # genre = "0"
    # platform = "blogger"
    # # stacking_min = configCall.stacking_min
    # # stacking_max = configCall.stacking_max
    # # alt_text = configCall.stacking_text
    # # start = 0
    # # end = 2000
    # # group = "all"
    # # blog.main(genre, platform, stacking_min, stacking_max, alt_text, group, start, end)
    # this_links = ["https://udl.forem.com/?r=https://www.aitomitsu.com/how-much-is-camel-coffee/",
    #               "https://udl.forem.com/?r=https://www.awayaicchou.com/what-will-become-of-zozotown-stock-prices/ ",
    #               "https://udl.forem.com/?r=https://www.awayaicchou.com/what-will-be-the-price-of-japan-elevator/"]
    # alt_text = "雨の音を聞いて、花の匂いを嗅いでください"
    # title_alt = "雨の音を聞いて、花の匂いを嗅いでください"
    # cookie = "_note_session_v5=f8bf6b07d5717bdd08c897fc196e277a; XSRF-TOKEN=4_AOPncU6oSlwqV9y0ZughFOO_O2oYGuwU7ugdnOAqA; _gid=GA1.2.426161500.1731485738; fp=ba9b9ee4e345005739a4162c19bd18b44; _vid_v1=5c8732e375361b50a11aa1de7af167e1; _vid_v1=5c8732e375361b50a11aa1de7af167e1; _ga=GA1.1.553376880.1726304198; _ga_J9CPC3WE56=GS1.1.1731688073.23.1.1731688164.0.0.0"
    # proxies = "154.89.107.61:21318"
    #
    # arts = "起こったことは変えられないので、それについて考える時間を無駄にしないでください。先に進み、手放し、忘れてください。後で考えてみると、実際には何も問題はありません。"
    #
    # useragent = ""
    # note.post_to_note(arts, 0, cookie, useragent, proxies, this_links, title_alt, alt_text)

    # note.main(pcname, queue_url, genre, platform, stacking_min, stacking_max, title_alt, alt_text, sort, isarts,
    #      postingStyle, group, start, end)





