# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/16 00:47
@Author ： eblis
@File ：telegraSelenium.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import time
from datetime import datetime
import threading
base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from backendServices.src.awsMQ.amazonSQS import AmazonSQS


class postSpliceGo:
    def __init__(self):
        self.usego = otherUse()
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


        self.usego.sendlog(
            f"接收到的参数：genre:{genre}, platform:{platform}, stacking_min{stacking_min}, stacking_max{stacking_max},alt_text {alt_text},sort {sort}, postingStyle{postingStyle}, isarts{isarts}")
        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=1)
        # 第一步根据 platform 选用ads
        if platform == "blogger":
            adsUserList = self.siphon_ads(platform, group, eval(configCall.min_concurrent_user))

        elif platform == "note":
            adsUserList = self.siphon_ads(platform, group, eval(configCall.min_concurrent_user))
        elif platform == "telegra":
            adsUserList = self.siphon_ads(platform, eval(configCall.stacking_ads), eval(configCall.min_concurrent_user))

        else:
            return False

        self.usego.sendlog(f"adsUserList 结果：{adsUserList}")
        if adsUserList != []:
            # 第二步：拆分 拼接信息
            all_links_list_group = self.split_links(genre, platform, sort, start, end, stacking_min, stacking_max)

        # 第 3 步： 进一步 处理
            all_res = self.run(isarts, postingStyle, platform, genre, adsUserList, all_links_list_group, title_alt,
                               alt_text)

            sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
            self.aws_sqs.deleteMSG(queue_url)
            return all_res

        else:

            sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
            self.aws_sqs.deleteMSG(queue_url)

            return None

    def run(self, isarts, postingStyle, platform, genre, adsUserList, all_links_list_group, title_alt, alt_text):
        """
            @Datetime ： 2024/11/2 12:56
            @Author ：eblis
            @Motto：简单描述用途
        """
        all_res = []
        mun = 0
        mm = 0
        runTure = True
        while len(all_links_list_group) > 0 and runTure:
            self.usego.sendlog(f"第 {mun} 执行开始,剩余{len(all_links_list_group) - 1} 组数据待处理")
            if len(adsUserList) > mm:
                this_res_list = []
                bad_run_list = []
                threads = []

                this_group_ads = adsUserList[mm]
                self.usego.sendlog(f"这组ads选手分别是{this_group_ads}")
                this_go = min(len(this_group_ads), len(all_links_list_group))
                self.usego.sendlog(f"需要建立{this_go} 个 线程")
                for i in range(this_go):
                    if int(isarts) == 0:
                        arts = self.read_file()
                    else:
                        arts = None
                    user = self.usego.changeDict(this_group_ads[i])
                    this_links = all_links_list_group[i]
                    self.usego.sendlog(f"这组 使用的是{user},发布的是{this_links} 链接")
                    # 获取文章内容链接
                    content = self.get_links(arts, postingStyle, this_links, alt_text)
                    self.usego.sendlog(f"本次使用的内容是：{content}")
                    if platform == "blogger":
                        t = threading.Thread(target=self.post_to_blogger, args=(this_res_list, this_links, all_links_list_group, bad_run_list, user["bloggerID"], user["adsID"], title_alt, content))
                    elif platform == "note":
                        t = threading.Thread(target=self.post_to_note, args=(this_res_list, this_links, all_links_list_group, bad_run_list, user["cookie"], user["useragent"], user["proxies"], title_alt, content))

                    else:
                        t = threading.Thread(target=self.post_to_telegra,
                                             args=(this_res_list, this_links, all_links_list_group, bad_run_list,  user, title_alt, postingStyle, alt_text, arts))


                    threads.append(t)
                    t.start()
                    time.sleep(3)

                for thread in threads:
                    thread.join()

                self.usego.sendlog(f"这波Thread 执行完了：{this_res_list}")


                if this_res_list != []:
                    self.usego.sendlog(f"将数据同步存放数据库")

                    self.usego.sendlog(f"{self.save_datebase(this_res_list, genre, platform)}")

                self.usego.sendlog(f"总剩余：{len(all_links_list_group)}")

                all_links_list_group.extend(bad_run_list)
                bad_run_list.clear()
                self.usego.sendlog(f"最终剩余：{len(all_links_list_group)}")

                for link in this_res_list:
                    if link not in all_res:
                        all_res.append(link)

                mm = mm + 1
                mun = mun + 1

            else:
                if platform in ["blogger","note"]:
                    self.usego.sendlog(f"{adsUserList} 都跑过了")
                    runTure = False
                else:
                    self.usego.sendlog(f"初始化一下数据，跑空")
                    mm = 0


    def post_to_blogger(self,this_res_list, this_links, all_links_list_group, bad_run_list, bloggerID, adsUser, title_alt, content):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        from backendServices.src.socialPlatforms.bloggerGO.bloggerSeleniumGO import bloggerSeleniumGO
        blog = bloggerSeleniumGO()
        with threading.Lock():
            result = blog.run(bloggerID, adsUser, title_alt, content)
            if result:
                if "git.html" not in result:
                    this_res_list.append(result)
                    all_links_list_group.remove(this_links)
                    self.usego.sendlog(f"剩余：{len(all_links_list_group)}")

                    self.del_run_links(this_links)
                else:
                    self.usego.sendlog(f"丢弃结果: {result}，因为它包含 'git.html'")
            else:
                bad_run_list.append(this_links)


    def post_to_note(self,this_res_list, this_links, all_links_list_group, bad_run_list, cookie, useragent, proxies, title_alt, content):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        from backendServices.src.socialPlatforms.noteGO.notePostText import notePostText
        note = notePostText()
        with threading.Lock():
            result = note.run(cookie, useragent, proxies, title_alt, content)
            if result:
                this_res_list.append(result)
                all_links_list_group.remove(this_links)
                print(f"剩余：{len(all_links_list_group)}")

                self.del_run_links(this_links)
            else:
                bad_run_list.append(this_links)



    def post_to_telegra(self, this_res_list, this_links, all_links_list_group, bad_run_list,  user, title_alt, postingStyle, alt_text, arts):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        from backendServices.src.socialPlatforms.telegraGO.telegraSelenium import telegraSelenium
        telegra = telegraSelenium()
        with threading.Lock():
            result = telegra.run(user,title_alt, postingStyle, this_links, alt_text, arts)
            if result:
                this_res_list.append(result)
                all_links_list_group.remove(this_links)
                print(f"剩余：{len(all_links_list_group)}")
            else:
                self.usego.sendlog(f"执行失败了，{this_links} 这些需要回炉再造")
                bad_run_list.append(this_links)


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
    def del_run_links(self, links):
        """
            @Datetime ： 2024/10/28 02:10
            @Author ：eblis
            @Motto：从数据库中删除以使用的连接
        """
        # self.usego.sendlog(f"本次要删除 ：{len(links)} 条数据")
        query = {"url": {"$in": links}}
        sql_data = self.mossql.splicing_interim_delet("seo_external_links_post", query=query, multiple=True,
                                                      clear_all=False)
        self.usego.sendlog(f"删除结果：{sql_data}")

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
                # self.usego.sendlog(f"这条连接是：{link}")
                link = link.strip('\n')
                this_atab = f"""<a href="{link}" target="_blank">{alt_text}</a>&nbsp"""
                all_atab += this_atab
        elif int(postingStyle) == 1:
            for link in this_links:
                # self.usego.sendlog(f"这条连接是：{link}")
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


    def siphon_ads(self, platform, group, group_size):
        """
            @Datetime ： 2024/10/28 01:42
            @Author ：eblis
            @Motto：简单描述用途
        """
        if platform == "blogger":
            if group == "all":
                sql_data = self.ssql.blogger_info_select_sql()
            else:
                sql_data = self.ssql.blogger_info_select_sql(group=group)

            if "sql 语句异常" not in str(sql_data):
                lst = [{'adsID': item[3], 'bloggerID': item[5]} for item in sql_data]
                # lst = [item[3] for item in sql_data]
                return [lst[i:i + group_size] for i in range(0, len(lst), group_size)]
            else:
                return []
        elif platform == "note":
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
        elif platform == "telegra":
            self.usego.sendlog(f"进来的 group：{group}")
            return [group[i:i + group_size] for i in range(0, len(group), group_size)]
        else:
            return []


    def split_links(self, genre, platform, sort, start, end, stacking_min, stacking_max):
        """
            @Datetime ： 2024/11/25 23:24
            @Author ：eblis
            @Motto：简单描述用途
        """
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
                all_links_list = self.siphon_links(all_links, stacking_min, stacking_max)

                self.usego.sendlog(f"拆分为：{len(all_links_list)} 组")
                return all_links_list
            else:
                return None
        else:
            return None

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


if __name__ == '__main__':
    pass

