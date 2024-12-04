# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/25 20:45
@Author ： eblis
@File ：post_sql_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import re
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import time
from datetime import datetime
import threading

from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse

from backendServices.src.awsMQ.amazonSQS import AmazonSQS

import middleware.public.configurationCall as configCall

class postSqlArticle():
    def __init__(self):
        self.artsql = article_sqlGO()
        self.ssql = basis_sqlGO()
        self.usego = otherUse()
        self.aws_sqs = AmazonSQS()


    def main(self, pcname, queue_url, platform, group, post_max, sortID, type,  commission, isAI, user,language, isSecondary):
        """
            @Datetime ： 2024/11/18 22:19
            @Author ：eblis
            @Motto：简单描述用途
        """
        self.usego.sendlog(
            f"接收到的参数：platform:{platform}, group:{group}, post_max:{post_max}, sortID:{sortID},type:{type}, commission:{commission}, isAI:{isAI}, user:{user}, language:{language}")
        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=1)
        # 第一步根据 platform 选用ads
        if platform == "blogger":
            adsUserList = self.siphon_ads(platform, group, eval(configCall.min_concurrent_user))
        elif platform == "note":
            adsUserList = self.siphon_ads(platform, group, eval(configCall.min_concurrent_user))
        elif platform == "telegra":
            adsUserList = self.siphon_ads(platform, eval(configCall.stacking_ads), eval(configCall.min_concurrent_user))
        else:
            adsUserList = []
        self.usego.sendlog(f"adsUserList 结果：{len(adsUserList)}")
        if adsUserList != []:

            # 第二步：提取符合添加的 文章
            artList = self.witchArticle(sortID, type,  commission, isAI, user, language)
            self.usego.sendlog(f"artList 结果：{len(artList)}")
            if artList != []:
                # self.usego.sendlog(f"这波数据有 {len(artList)} 文章， 以及{len(adsUserList)} 账号")
                # 第3步：将已在相同平台相同 账号 发布过的文章 过滤掉
                post_read_list = self.secondaryProcessing(platform, post_max,  artList, adsUserList)
                self.usego.sendlog(f"post_read_list:{len(post_read_list)}")
                # new_post_read_list = []
                if int(isSecondary) == 0:
                    print("二次创作")
                    from backendServices.src.articleSome.public.aiGO import aiGO
                    aigo = aiGO()
                    for i in range(len(post_read_list)):
                        print(f"post_read_list[i],{post_read_list[i]['content']}")
                        content = self.usego.normalize_text(post_read_list[i]['content'])
                        prompt = f"""需求：阅读 {content} 并按以下要求优化后输出：1. **内容拆分**：将原文内容拆分为合理的短句或词组，以便进行同义词或近义词的替换。2. **同义词替换**：在不改变原文表达的意思情况下，使用同义词或近义词进行替换。3. **保持段落风格**：确保文段的结构和风格与原文一致。4. **保持原文语言**：确保所用语言与原文一致。"""
                        new_content = self.change_html(prompt)
                        newContent = aigo.run(new_content)
                        if newContent is not None:
                            post_read_list[i]['content'] = newContent
                        else:
                            print("二次创作失败，使用原文")

                else:
                    print("直接开跑，不浪费时间")

            #     第4步：开跑：
                all_res = self.run(platform, adsUserList, post_read_list)
            else:
                self.usego.sendlog(f"没有符合 {sortID}, {type}, {commission}, {isAI}, {user} 的文章")
                all_res = None

        else:
            self.usego.sendlog("没有可用 用户")
            all_res = None

        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
        self.aws_sqs.deleteMSG(queue_url)
        return all_res





    def run(self, platform, adsUserList, post_read_list):
        """
            @Datetime ： 2024/11/2 12:56
            @Author ：eblis
            @Motto：简单描述用途
        """
        self.usego.sendlog(f"platform：{platform},adsUserList：adsUserList{adsUserList}，post_read_list：{adsUserList}")
        all_res = []
        mun = 0
        mm = 0
        runTure = True
        while len(post_read_list) > 0 and runTure:
            self.usego.sendlog(f"第 {mun} 执行开始,剩余{len(post_read_list) - 1} 组数据待处理")
            if len(adsUserList) > mm:
                this_res_list = []
                this_history_list = []
                bad_run_list = []
                threads = []

                this_group_ads = adsUserList[mm]
                self.usego.sendlog(f"这组ads选手分别是{this_group_ads}")
                this_go = min(len(this_group_ads), len(post_read_list))
                self.usego.sendlog(f"需要建立{this_go} 个 线程")

                for i in range(this_go):
                    user = self.usego.changeDict(this_group_ads[i])
                    this_post_data = self.usego.changeDict(post_read_list[i])
                    self.usego.sendlog(f"这组 使用的是{user},发布的是{this_post_data } 信息")
                    if platform == "blogger":
                        t = threading.Thread(target=self.post_to_blogger, args=(platform, this_res_list, this_history_list, bad_run_list, post_read_list, this_post_data,user["id"],  user["bloggerID"], user["adsID"]))
                    elif platform == "note":
                        t = threading.Thread(target=self.post_to_note, args=(
                        platform, this_res_list, this_history_list,  bad_run_list, post_read_list, this_post_data, user["id"], user["cookie"], user["useragent"], user["proxies"]))

                    else:
                        t = threading.Thread(target=self.post_to_telegra,
                                             args=(platform, this_res_list, this_history_list, post_read_list, this_post_data, user))

                    threads.append(t)
                    t.start()
                    time.sleep(3)

                for thread in threads:
                    thread.join()

                # self.usego.sendlog(f"这波Thread 执行完了：{this_res_list}")

                if this_res_list != []:
                    self.usego.sendlog(f"将this_res_list数据同步存放数据库，{this_res_list}")
                    self.usego.sendlog(f"将this_history_list数据同步存放数据库，{this_history_list}")

                    self.save_datebase(this_res_list, this_history_list)

                self.usego.sendlog(f"总剩余：{len(post_read_list)}")

                post_read_list.extend(bad_run_list)
                bad_run_list.clear()
                self.usego.sendlog(f"最终剩余：{len(post_read_list)}")

                for link in this_res_list:
                    if link not in all_res:
                        all_res.append(link)

                mm = mm + 1
                mun = mun + 1

            else:
                if platform in ["blogger", "note"]:
                    self.usego.sendlog(f"{adsUserList} 都跑过了")
                    runTure = False
                else:
                    self.usego.sendlog(f"初始化一下数据，跑空")
                    mm = 0

        self.usego.sendlog("跑完了")
        return all_res


    def change_html(self, html_content):
        """
            @Datetime ： 2024/12/4 20:23
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 要移除的标签列表
        html_tags = ["<!DOCTYPE html>", "<html>", "</html>", "<head>", "</head>", "<body>", "</body>", "<title>",
                     "</title>"]

        # 通过正则表达式移除指定标签
        for tag in html_tags:
            html_content = re.sub(re.escape(tag), "", html_content, flags=re.IGNORECASE)


        return html_content.strip()



    def post_to_blogger(self, platform, this_res_list,  this_history_list, bad_run_list, post_read_list, this_post_data, user_id, bloggerID, adsUser):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        from backendServices.src.socialPlatforms.bloggerGO.bloggerSeleniumGO import bloggerSeleniumGO
        blog = bloggerSeleniumGO()
        this_history = []
        # 获取当前时间
        now = datetime.now()
        # 格式化为年月日时分秒
        create_at = now.strftime("%Y-%m-%d %H:%M:%S")
        with threading.Lock():
            result = blog.run(bloggerID, adsUser, this_post_data["title"], this_post_data["content"])
            if result:
                if "git.html" not in result:
                    # 保留原有的 this_post_data["id"]
                    this_history.append(this_post_data["id"])
                    this_history.append(user_id)
                    # 将 this_result 数据写入 this_history，确保顺序不被打乱
                    this_result = [platform, result, create_at]  # 保证顺序正确
                    this_history_list.append(tuple(this_history))
                    this_res_list.append(tuple(this_result))
                    post_read_list.remove(this_post_data)
                self.usego.sendlog(f"剩余：{len(post_read_list)} 文章没发")

            else:
                self.usego.sendlog(f"执行失败了，{this_post_data} 这些需要回炉再造")
                bad_run_list.append(this_post_data)


    def post_to_note(self, platform, this_res_list, this_history_list,  bad_run_list, post_read_list, this_post_data,user_id, cookie, useragent, proxies):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        from backendServices.src.socialPlatforms.noteGO.notePostText import notePostText
        note = notePostText()
        this_history = []
        # 获取当前时间
        now = datetime.now()
        # 格式化为年月日时分秒
        create_at = now.strftime("%Y-%m-%d %H:%M:%S")
        with threading.Lock():
            result = note.run(cookie, useragent, proxies, this_post_data["title"], this_post_data["content"])
            if result:

                # 保留原有的 this_post_data["id"]
                this_history.append(this_post_data["id"])
                this_history.append(user_id)
                # 将 this_result 数据写入 this_history，确保顺序不被打乱
                this_result = [platform, result, create_at]  # 保证顺序正确

                # 这里我们将 this_result 中的元素追加到 this_history 中
                this_history.extend(this_result)
                this_history_list.append(tuple(this_history))
                this_res_list.append(tuple(this_result))
                post_read_list.remove(this_post_data)
                self.usego.sendlog(f"剩余：{len(post_read_list)} 文章没发")
            else:
                self.usego.sendlog(f"执行失败了，{this_post_data} 这些需要回炉再造")
                bad_run_list.append(this_post_data)



    def post_to_telegra(self, platform, this_res_list, this_history_list, post_read_list, this_post_data, adsUser):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        from backendServices.src.socialPlatforms.telegraGO.telegraSeleniumGO import telegraSeleniumGO
        telegraGO = telegraSeleniumGO()
        self.usego.sendlog(f"开始发 {platform}")
        # 创建一个包含目标链接的列表
        to_remove = ["https://telegra.ph", "https://telegra.ph/"]
        this_history = []
        # 获取当前时间
        now = datetime.now()
        # 格式化为年月日时分秒
        create_at = now.strftime("%Y-%m-%d %H:%M:%S")
        with threading.Lock():
            result = telegraGO.run(adsUser, this_post_data["title"], this_post_data["content"])
            if result:
                if result not in to_remove:
                    # 保留原有的 this_post_data["id"]
                    this_history.append(this_post_data["id"])
                    this_history.append("")

                    # 将 this_result 数据写入 this_history，确保顺序不被打乱
                    this_result = [platform, result, create_at]  # 保证顺序正确

                    # 这里我们将 this_result 中的元素追加到 this_history 中
                    this_history.extend(this_result)
                this_history_list.append(tuple(this_history))
                this_res_list.append(tuple(this_result))
                post_read_list.remove(this_post_data)
                self.usego.sendlog(f"剩余：{len(post_read_list)} 文章没发")

            else:
                self.usego.sendlog(f"执行失败了")


    def secondaryProcessing(self, platform, post_max, artList, adsUserList):
        """
            @Datetime ： 2024/11/29 21:16
            @Author ：eblis
            @Motto：将未发布文章分配到每个用户，即使文章不足。
        """
        # 获取历史记录
        historyL = self.historyArticle()

        # 初始化用户分配结果
        forReleaseArt = []

        # 如果 historyL 为空，则直接为每个用户分配一篇文章
        self.usego.sendlog(f"historyL 结果 {historyL}")
        if platform == "telegra":
            article = artList[:min(post_max, len(artList))]
            forReleaseArt.extend(article)
            return forReleaseArt
        else:
            if not historyL:

                self.usego.sendlog(f"有{len(adsUserList)}组，准备分配{len(artList)}")
                for adsitem in adsUserList:
                    self.usego.sendlog(f"这组 有 {len(adsitem)} 个用户")
                    for i, ads_user in enumerate(adsitem):
                        # 如果文章不足，则循环分配文章
                        self.usego.sendlog(f"第{i}个用户，总用户：{len(artList)}")
                        article = artList[i % len(artList)]
                        forReleaseArt.append(article)
                return forReleaseArt

            # 筛选出指定平台的历史记录，按用户分组
            platform_history = [
                record for record in historyL if record.get("platform") == platform
            ]
            user_published_articles = {}
            for record in platform_history:
                user_id = record.get("accountID")
                if user_id not in user_published_articles:
                    user_published_articles[user_id] = set()
                user_published_articles[user_id].add(record.get("articleID"))

            # 遍历用户并确保每个用户分配一篇文章
            unposted_articles = [art for art in artList]  # 拷贝文章列表
            for adsitem in adsUserList:
                for i, ads_user in enumerate(adsitem):
                    user_id = ads_user.get("id")
                    published_articles = user_published_articles.get(user_id, set())

                    # 为该用户选择未发布的文章
                    if unposted_articles:
                        selected_article = unposted_articles.pop(0)
                    else:
                        # 如果文章不足，则循环分配已分配的文章
                        selected_article = artList[i % len(artList)]

                    forReleaseArt.append(selected_article)

            return forReleaseArt

    def historyArticle(self):
        """
            @Datetime ： 2024/11/29 20:44
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.artsql.post_article_history_list_sql()
        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'articleID': item[1], 'accountID': item[2], 'platform': item[3], 'succeedUrl': item[4]} for item in sql_data]

                return resdatas
            except:
                return []
        else:
            return []


    def save_datebase(self, datalist, historylist):
        """
            @Datetime ： 2024/10/27 14:06
            @Author ：eblis
            @Motto：保存到数据库——seo_result_301_links
        """
        result = self.artsql.post_article_result_batch_insert(datalist)
        time.sleep(5)
        historyResult = self.artsql.post_articlehistory_batch_insert(historylist)
        self.usego.sendlog(f"执行结果:{result}, {historyResult}")

    
    def witchArticle(self, sortID, type, commission, isAI, user,language):
        """
            @Datetime ： 2024/11/29 14:40
            @Author ：eblis
            @Motto：跟要求读取数据库文章信息
        """
        if int(commission) == 1:
            user = None
        else:
            user = user[0]
        sql_data = self.artsql.article_select_sql(sortID=sortID, type=type, commission=commission, isAI=isAI, user=user, language=language)
        if "sql 语句异常" not in str(sql_data):
            try:
                resdatas = [{'id': item[0], 'title': item[5], 'content': item[6]} for item in sql_data]

                return resdatas

            except:
                return []
        else:
            return []

    def read_file(self):
        """
            @Datetime ： 2024/11/5 02:55
            @Author ：eblis
            @Motto：读取本地文本内容
        """
        # 存储已经读取过的文件名，避免重复读取
        read = []
        all_files = os.listdir(configCall.splicing_articie_path)

        # 去除已读取过的文件名
        unread_files = [f for f in all_files if f not in read]

        if not unread_files:
            self.usego.sendlog("所有文件已读取完毕,那就重新来")
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
                lst = [{'id': item[0], 'adsID': item[3], 'bloggerID': item[5]} for item in sql_data]
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
                lst = [{'id': item[0], 'username': item[4], 'proxies': item[7], 'useragent': item[8],
                        'cookie': item[9]} for item in sql_data]
                return [lst[i:i + group_size] for i in range(0, len(lst), group_size)]

            else:
                return []
        elif platform == "telegra":
            self.usego.sendlog(f"进来的 group：{group}")
            return [group[i:i + group_size] for i in range(0, len(group), group_size)]
        else:
            return []



if __name__ == '__main__':
    po = postSqlArticle()
    pcname = "this_mac_1_not"
    queue_url = "/"
    platform = "telegra"
    group = "all"
    post_max = 10
    sortID = 4
    type = "Html"
    commission = 1
    isAI = 0
    user = ''
    isSecondary = 0
    language = ""

    po.main(pcname, queue_url, platform, group, post_max, sortID, type, commission, isAI, user, language, isSecondary)