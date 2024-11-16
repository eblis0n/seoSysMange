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

import threading
from middleware.deviceManage.adsDevice import adsDevice
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from backendServices.src.awsMQ.amazonSQS import AmazonSQS


class notePostText:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()
        self.aws_sqs = AmazonSQS()

    def main(self, pcname, queue_url, genre, platform, stacking_min, stacking_max, title_alt, alt_text, sort, isarts,
             postingStyle, group, start, end):
        """
            @Datetime ： 2024/10/26 00:09
            @Author ：eblis
            @Motto：简单描述用途
        """

        print(
            f"接收到的参数：genre{genre}, platform{platform}, stacking_min{stacking_min}, stacking_max{stacking_max},alt_text {alt_text},sort {sort}, postingStyle{postingStyle}, isarts{isarts}")
        # sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=1)
        userlist = self.siphon_user(group, eval(configCall.min_concurrent_user))

        if userlist != []:
            query = {
                "genre": str(genre),
                "platform": str(platform),
                "sort": str(sort),
            }
            sql_data = self.mossql.splicing_interim_findAll("seo_external_links_post", query, start=int(start),
                                                            end=int(end))

            if sql_data is not None:
                all_links = [data["url"] for data in sql_data] if sql_data else []

                if all_links:
                    alll_links_list = self.siphon_links(all_links, stacking_min, stacking_max)

                    print(f"拆分为：{len(alll_links_list)} 组")

                    all_res = self.run(isarts, postingStyle, platform, genre, userlist, alll_links_list, title_alt,
                                       alt_text)

                    sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
                    self.aws_sqs.deleteMSG(queue_url)
                    return all_res

        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
        self.aws_sqs.deleteMSG(queue_url)

        return None

    def run(self, isarts, postingStyle, platform, genre, userlist, alll_links_list, title_alt, alt_text):
        """
            @Datetime ： 2024/11/2 12:56
            @Author ：eblis
            @Motto：简单描述用途
        """
        all_res = []
        mun = 0
        mm = 0
        runTure = True
        while len(alll_links_list) > 0 and runTure:
            print(f"第 {mun} 执行开始,剩余{len(alll_links_list) - 1} 组数据待处理")
            if len(userlist) > mm:
                this_res_list = []
                bad_run_list = []
                threads = []
                this_group_user = userlist[mm]
                print(f"这组user选手分别是{this_group_user}")
                this_go = min(len(this_group_user), len(alll_links_list))
                print(f"需要建立{this_go} 个 线程")
                for i in range(this_go):
                    if int(isarts) == 0:
                        arts = self.read_file()
                    else:
                        arts = None
                    user = self.usego.changeDict(this_group_user[i])
                    link = alll_links_list[i]
                    print(f"这组 使用的是{user},发布的是{link} 链接")

                    t = threading.Thread(target=self.post_wrapper, args=(
                    arts, postingStyle, this_res_list, link, alll_links_list, bad_run_list,  user["cookie"], user["useragent"],
                    user["proxies"], title_alt, alt_text))

                    threads.append(t)
                    t.start()
                    time.sleep(3)

                for thread in threads:
                    thread.join()

                print(f"这波Thread 执行完了：{this_res_list}")

                self.save_res(this_res_list)

                if this_res_list != []:
                    print(f"将数据同步存放数据库")

                    print(f"{self.save_datebase(this_res_list, genre, platform)}")

                print(f"总剩余：{len(alll_links_list)}")

                alll_links_list.extend(bad_run_list)
                bad_run_list.clear()
                print(f"最终剩余：{len(alll_links_list)}")

                for link in this_res_list:
                    if link not in all_res:
                        all_res.append(link)

                mm = mm + 1
                mun = mun + 1

            else:
                print(f"{userlist} 都跑过了")
                runTure = False

    def post_wrapper(self, arts, postingStyle, result_list, this_links, all_list, bad_run_list, cookie, useragent, proxies,
                     title_alt, alt_text):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        with threading.Lock():
            result = self.post_to_note(arts, postingStyle, cookie, useragent, proxies, this_links, title_alt, alt_text)
            if result:
                result_list.append(result)
                all_list.remove(this_links)
                print(f"剩余：{len(all_list)}")

                self.del_run_links(this_links)
            else:
                bad_run_list.append(this_links)

    def post_to_note(self, arts, postingStyle, cookie, useragent, proxies, this_links, title_alt, alt_text):

        # 获取文章内容链接
        bodydata = self.get_links(arts, postingStyle, this_links, alt_text)
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
        print("执行信息",js_path, str(id), cookie, useragent, file, proxies)

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

    def read_file(self):
        """
            @Datetime ： 2024/11/5 02:55
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 存储已经读取过的文件名，避免重复读取
        read = []
        all_files = os.listdir(configCall.splicing_articie_path)

        # 去除已读取过的文件名
        unread_files = [f for f in all_files if f not in read]

        if not unread_files:
            print("所有文件已读取完毕,那就重新来")
            read.clear()
            filename = self.usego.randomChoice(all_files)
        else:
            filename = self.usego.randomChoice(unread_files)

        file_path = f"{configCall.splicing_articie_path}/{filename}"

        # 读取文件内容并记录文件名
        with open(file_path, 'r', encoding='utf-8') as f:
            arts = f.read()
            read.append(filename)  # 将文件名添加到已读列表中

        return arts

    def get_links(self, arts, postingStyle, this_links, alt_text):
        """
            @Datetime ： 2024/10/30 16:56
            @Author ：eblis
            @Motto：简单描述用途
        """
        # print(type(arts), arts)
        all_atab = ''
        if arts is not None and arts != "None":
            this_atab = f"""<p>{arts}</p>&nbsp"""
            all_atab += this_atab

        if int(postingStyle) == 0:
            for link in this_links:
                # print(f"这条连接是：{link}")
                link = link.strip('\n')
                this_atab = f"""<a href="{link}" target="_blank">{alt_text}</a>&nbsp"""
                all_atab += this_atab
        elif int(postingStyle) == 1:
            for link in this_links:
                # print(f"这条连接是：{link}")
                link = link.strip('\n')
                this_atab = f"""<p><a href="{link}" target="_blank">{link}</a></p>"""
                all_atab += this_atab
        else:
            for index, link in enumerate(this_links):
                link = link.strip('\n')
                if index < len(this_links):
                    this_atab = f"""<p>{link}</p>"""
                    all_atab += this_atab
                else:
                    this_atab = f"""<p><a href="{link}" target="_blank">{link}</a></p>"""
                    all_atab += this_atab
        return all_atab

    def siphon_user(self, group, group_size):
        """
            @Datetime ： 2024/10/28 01:42
            @Author ：eblis
            @Motto：简单描述用途
        """
        if group == "all":
            sql_data = self.ssql.note_users_info_select_sql()
        else:
            sql_data = self.ssql.note_users_info_select_sql(group=group)

        if "sql 语句异常" not in str(sql_data):
            lst = [{'username': item[4], 'proxies': item[7], 'useragent': item[8],
                     'cookie': item[9]} for item in sql_data]
            return [lst[i:i + group_size] for i in range(0, len(lst), group_size)]

        else:
            return []

    def siphon_links(self, all_links, rmin, rmax):
        this_run_list = []
        allLinks = [item for item in all_links if item != '\n']

        while allLinks:
            num_links_to_add = min(len(allLinks), self.usego.randomRandint(int(rmin), int(rmax)))
            selected_links = self.usego.redome_sample(allLinks, num_links_to_add)
            this_run_list.append(selected_links)
            for link in selected_links:
                allLinks.remove(link)

        return this_run_list

    def del_run_links(self, links):
        """
            @Datetime ： 2024/10/28 02:10
            @Author ：eblis
            @Motto：简单描述用途
        """
        # print(f"本次要删除 ：{len(links)} 条数据")
        query = {"url": {"$in": links}}
        sql_data = self.mossql.splicing_interim_delet("seo_external_links_post", query=query, multiple=True,
                                                      clear_all=False)
        print(f"删除结果：{sql_data}")

    def save_res(self, urls):
        print(f"本次需要保存的数据有{len(urls)},{urls}")
        formatted_now = datetime.now().strftime("%Y%m%d")
        file_name = f"blogger_result_{formatted_now}.txt"
        today_file = self.usego.make_file(configCall.blogger_result, file_name)
        with open(today_file, 'a+') as f:
            for url in urls:
                f.write(f"{url}\n")

    def save_datebase(self, urls, genre, platform):
        """
            @Datetime ： 2024/10/27 14:06
            @Author ：eblis
            @Motto：保存到数据库——seo_result_301_links
        """

        # 获取当前时间
        now = datetime.now()

        # 格式化为年月日时分秒
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        new_links_list = []
        for url in urls:
            this_dat = {
                "url": f"{url}",
                "platform": f"{platform}",
                "genre": f"{genre}",
                "created_at": created_at
            }
            new_links_list.append(this_dat)
        result = self.mossql.splicing_interim_insert_batch("seo_result_301_links", new_links_list)
        if result is not None:  # 修改这里，检查 result 是否为 None
            return f"生成 {len(new_links_list)} 个新链接，已入库"
        else:
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
    note = notePostText()
    # 调试，通过配置文件修改
    genre = "0"
    platform = "blogger"
    # stacking_min = configCall.stacking_min
    # stacking_max = configCall.stacking_max
    # alt_text = configCall.stacking_text
    # start = 0
    # end = 2000
    # group = "all"
    # blog.main(genre, platform, stacking_min, stacking_max, alt_text, group, start, end)
    this_links = ["https://udl.forem.com/?r=https://www.aitomitsu.com/how-much-is-camel-coffee/",
                  "https://udl.forem.com/?r=https://www.awayaicchou.com/what-will-become-of-zozotown-stock-prices/ ",
                  "https://udl.forem.com/?r=https://www.awayaicchou.com/what-will-be-the-price-of-japan-elevator/"]
    alt_text = "雨の音を聞いて、花の匂いを嗅いでください"
    title_alt = "雨の音を聞いて、花の匂いを嗅いでください"
    cookie = "_note_session_v5=f8bf6b07d5717bdd08c897fc196e277a; XSRF-TOKEN=4_AOPncU6oSlwqV9y0ZughFOO_O2oYGuwU7ugdnOAqA; _gid=GA1.2.426161500.1731485738; fp=ba9b9ee4e345005739a4162c19bd18b44; _vid_v1=5c8732e375361b50a11aa1de7af167e1; _vid_v1=5c8732e375361b50a11aa1de7af167e1; _ga=GA1.1.553376880.1726304198; _ga_J9CPC3WE56=GS1.1.1731688073.23.1.1731688164.0.0.0"
    proxies = "154.89.107.61:21318"

    arts = "起こったことは変えられないので、それについて考える時間を無駄にしないでください。先に進み、手放し、忘れてください。後で考えてみると、実際には何も問題はありません。"

    useragent = ""
    note.post_to_note(arts, 0, cookie, useragent, proxies, this_links, title_alt, alt_text)

    # note.main(pcname, queue_url, genre, platform, stacking_min, stacking_max, title_alt, alt_text, sort, isarts,
    #      postingStyle, group, start, end)





