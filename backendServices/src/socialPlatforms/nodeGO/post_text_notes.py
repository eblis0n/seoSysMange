# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/8/20 22:26
@Author ： eblis
@File ：post_text_self.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import os
import sys
import time

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
import requests
import json
from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
import middleware.public.configurationCall as configCall

class notesTextPost():
    def __init__(self):
        self.usego = otherUse()
        self.ssql = basis_sqlGO()


    def run(self,noteuser, cookie, proxies):
        """
            @Datetime ： 2024/8/21 16:25
            @Author ：eblis
            @Motto：简单描述用途
        """
        self.usego.sendlog(f"本次任务由：{noteuser} 执行")
        try:
            sql_data =self.ssql.note_article_select_sql(noteuser)
        except Exception as e:
            self.usego.sendlog(f"请求数据库出现异常:{e}")
        else:
            if "sql 语句异常" not in str(sql_data):
                resdatas = [{'id': item[0], 'noteuser': item[1], 'keyword': item[2], 'title': item[3], 'content': item[4]} for item in sql_data]
                resdata = self.usego.randomChoice(resdatas)
                self.usego.sendlog(f"{noteuser}还有{len(resdatas)} 篇文章可用")
                # self.usego.sendlog(f"本次准备使用{resdata['title']},进行发布")

                title = f"""{resdata['title']}"""
                bodydata = f"""{resdata['content']}"""
                body_length = len(bodydata)

                headers = {'Content-Type': 'application/json',
                           'cookie': f"{cookie}",
                           'referer': 'https://editor.note.com/',
                           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                           'x-requested-with': 'XMLHttpRequest'
                           }  # 设置 HTTP 头部为 JSON

                self.usego.sendlog(f"当前代理获取结果{proxies}")
                proxies_json = json.loads(proxies)


                # 第一步：进入发帖页面
                dd = self.text_notes(headers, proxies_json)
                try:
                    self.usego.sendlog(f"进入编辑状态请求结果：{dd['data']}")
                except Exception as e:
                    self.usego.sendlog(f"出现了{e}")
                else:
                    self.usego.sendlog("没有异常，les~go~")
                    # # 第二步上传顶部图片
                    # imgage = self.post_imgage(dd['data']['id'], cookie, filepath, filenanme, proxies)
                    # print("imgage",imgage)
                    # 第三步:确认发送
                    get_post = self.post_text_go(dd['data']['id'], headers, proxies_json, dd['data']['slug'], bodydata, body_length,
                                                  title)
                    try:
                        self.usego.sendlog(f"发布结果：{get_post['data']}")
                    except:
                        self.usego.sendlog(f"fget_post,{get_post}")
                    else:
                    # print(get_post['data']['note_url'])
                        try:
                           self.ssql.note_article_update_sql(resdata["id"], get_post['data']['note_url'])
                        except Exception as e:
                            self.usego.sendlog(f'{resdata["id"]} 这篇文章发布了，但写入数据库失败')
                            self.usego.sendlog(f"请求数据库出现异常:{e}")
        return True




    def text_notes(self,headers,proxies):
            """
                @Datetime ： 2024/8/20 22:27
                @Author ：eblis
                @Motto：进入编辑页面
            """

            url = "https://note.com/api/v1/text_notes"

            data = {
                "template_key": "null".replace('"', "")  # 在 Python 中，None 对应于 JSON 的 null
            }

            if proxies is None:

                response = requests.post(url, headers=headers, data=json.dumps(data))
            else:
                try:
                    response = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxies, timeout=60)
                    self.usego.sendlog("成功使用代理")
                except:
                    response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 201:
                return response.json()
            else:
                self.usego.sendlog(f"{response.status_code}, {response.text}")
                return False

    # def post_imgage(self, id, cookie, filepath, filenanme, proxies):
    #     """
    #         @Datetime ： 2024/8/22 13:58
    #         @Author ：eblis
    #         @Motto：文章顶图
    #     """
    #     # 替换为你的文件路径
    #     # filepath = '/path/to/your/file.jpg'
    #     # 替换为你的接口URL
    #     url = "https://note.com/api/v1/image_upload/note_eyecatch"
    #     #
    #     headers = {
    #                 'cookie': f"{cookie}",
    #                 'referer': 'https://editor.note.com/',
    #                 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    #                 'x-requested-with': 'XMLHttpRequest'
    #                }  # 设置 HTTP 头部为 JSON
    #
    #     # 打开文件
    #     with open(f"{filepath}/{filenanme}", 'rb') as f:
    #         # 创建一个名为'file'的文件对象
    #         # print(f.read())
    #         files = {'file': f}
    #         # 创建一个包含其他字段的字典
    #         data = {'note_id': id, 'width': 1920, 'height': 1005}
    #         # 发送post请求
    #         if proxies is None:
    #             response = requests.post(url, headers=headers, files=files, data=data)
    #         else:
    #             try:
    #                 response = requests.post(url, headers=headers, files=files, data=data, proxies=proxies)
    #                 self.usego.sendlog("成功使用代理")
    #             except:
    #                 response = requests.post(url, headers=headers, files=files, data=data)
    #
    #
    #     if response.status_code == 201:
    #         return response.json()
    #     else:
    #         self.usego.sendlog(f"{response.status_code}, {response.text}")
    #         return False

    def post_text_go(self, id, headers, proxies, slug, bodydata, body_length, title):
        """
            @Datetime ： 2024/8/20 22:40
            @Author ：eblis
            @Motto：确认发送并返回url
        """
        self.usego.sendlog(f"开始")
        url = f"https://note.com/api/v1/text_notes/{id}"
        data = {
            "author_ids":[],
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

        self.usego.sendlog(f"传参：{url},{data},{proxies}")
        self.usego.sendlog(f"代理配置{type(proxies)},{proxies}")
        if proxies is None:
            response = requests.put(url, headers=headers, data=json.dumps(data))
        else:
            try:
                response = requests.put(url, headers=headers, data=json.dumps(data), proxies=proxies, timeout=60)
                self.usego.sendlog("成功使用代理")
            except Exception as e:
                # response = requests.put(url, headers=headers, data=json.dumps(data))
                self.usego.sendlog(f"代理失败原因{e}")
                time.sleep(3)
                self.usego.sendlog("再尝试一下使用代理")
                try:
                    response = requests.put(url, headers=headers, data=json.dumps(data), proxies=proxies, timeout=60)
                    self.usego.sendlog("成功使用代理")
                except Exception as e:
                    self.usego.sendlog(f"2次代理失败原因{e}")
                    response = requests.put(url, headers=headers, data=json.dumps(data))


        if response.status_code == 200:

            return response.json()
        else:
            self.usego.sendlog(f"{response.status_code}, {response.text}")
            return None




if __name__ == '__main__':
    notes = notesTextPost()
    cookie = '_gid=GA1.2.105596916.1724162854; fp=b6a32e1a802b58a36051a59ed9e07e4c7; _note_session_v5=34d5a35561709a3470fcafb81406f775; XSRF-TOKEN=7N-QAz-SLWSyyQHYIiN8USXGE0WGn6e2bZ6KcTa_tpU; _ga=GA1.1.1110361952.1722487453; _vid_v1=02d5caa3fc0c8f8b91357fbdc6237dba; _ga_J9CPC3WE56=GS1.1.1724301628.10.1.1724303406.0.0.0; _vid_v1=a76733f40a71eee09173346b36708038'
    noteuser = "Marilyn"

    proxies = {"http": "38.174.192.114:45123", "https": "38.174.192.114:45123"}
    notes.run(noteuser, cookie, proxies)





