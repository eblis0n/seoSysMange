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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.deviceManage.adsDevice import adsDevice
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from backendServices.src.awsMQ.amazonSQS import AmazonSQS

class telegraSelenium:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()


    def main(self, pcname, queue_url, genre, platform, stacking_min, stacking_max, title_alt, alt_text, sort, isarts,  postingStyle, group, start, end):

        """
            @Datetime ： 2024/10/26 00:09
            @Author ：eblis
            @Motto：genre 类型，platform：平台 isarts：是否贴文 postingStyle：A标签形式
        """
        self.usego.sendlog(f"接收到的参数：pcname:{pcname},genre:{genre}, platform:{platform}, stacking_min:{stacking_min}, stacking_max:{stacking_max},alt_text:{alt_text},sort:{sort}, postingStyle:{postingStyle}, isarts:{isarts}")

        # 将 执行pc 状态 修改
        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=1)
        self.usego.sendlog(f"pc执行结果{sql_data}")


        adsUserlist = self.siphon_adsuser(eval(configCall.stacking_ads), eval(configCall.min_concurrent_user))

        query = {
            "genre": str(genre),
            "platform": str(platform),
            "sort": str(sort),
        }
        sql_data = self.mossql.splicing_interim_findAll("seo_external_links_post", query,  start=int(start), end=int(end))
        aws_sqs = AmazonSQS()

        if sql_data is not None:
            all_links = [data["url"] for data in sql_data] if sql_data else []

            if all_links:
                alll_links_list = self.siphon_links(all_links, stacking_min, stacking_max)

                self.usego.sendlog(f"拆分为：{len(alll_links_list)} 组")

                all_res = self.run(isarts, postingStyle, platform, genre, adsUserlist, alll_links_list, title_alt, alt_text)
                sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
                aws_sqs.deleteMSG(queue_url)

                return all_res
        aws_sqs.deleteMSG(queue_url)
        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
        return None
    

    def run (self, isarts, postingStyle, platform, genre, adsUserlist, alll_links_list, title_alt, alt_text):
        all_res = []
        mun = 0
        mm = 0
        while len(alll_links_list) > 0:
            self.usego.sendlog(f"第 {mun} 执行开始,剩余{len(alll_links_list)} 组数据待处理")
            if len(adsUserlist) > mm:
                this_res_list = []
                threads = []
                bad_run_list = []
                is_run_list = []
                thisnoneads = adsUserlist[mm]
                self.usego.sendlog(f"这组ads选手分别是{thisnoneads}")
                this_go = min(len(thisnoneads), len(alll_links_list))
                self.usego.sendlog(f"需要建立{this_go} 个线程")
                for i in range(this_go):
                    if int(isarts) == 0:
                        arts = self.read_file()
                    else:
                        arts = None
                    user = thisnoneads[i]
                    link = alll_links_list[i]
                    self.usego.sendlog(f"{i}组使用的是 {user} 发布：{len(link)}, {link} 这些链接")
                    t = threading.Thread(target=self.post_to_wrapper,
                                         args=(arts, postingStyle, user, this_res_list, link, bad_run_list, is_run_list, title_alt, alt_text))

                    threads.append(t)
                    t.start()
                    time.sleep(3)

                for thread in threads:
                    thread.join()

                self.usego.sendlog(f"这波Thread 执行完了：{this_res_list}")

                # 创建一个包含目标链接的列表
                to_remove = ["https://telegra.ph", "https://telegra.ph/"]
                # 使用 for 循环遍历并删除
                this_res_list = [link for link in this_res_list if link not in to_remove]

                if this_res_list != []:

                    for link in this_res_list:
                        if link not in all_res:
                            all_res.append(link)

                    self.save_res(this_res_list)
                    self.usego.sendlog(f"将数据同步存放数据库")
                    self.usego.sendlog(f"{self.save_datebase(this_res_list, genre, platform)}")

                self.usego.sendlog(f"失败的：{len(bad_run_list)}")

                alll_links_list.extend(bad_run_list)
                bad_run_list.clear()
                self.usego.sendlog(f"最终剩余：{len(alll_links_list)}")
                self.usego.sendlog(f"将成功发送的数据，从数据库中移除")
                # 将成功发送的数据，从数据库中移除
                for link in is_run_list:
                    self.del_run_links(link)
                    alll_links_list.remove(link)
                is_run_list.clear()

                self.usego.sendlog(f"<--------------- end --------------- >")

                mm = mm + 1
                mun = mun + 1
            else:
                self.usego.sendlog(f"初始化一下数据，跑空")
                mm = 0

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



    def del_run_links(self, links):
        """
            @Datetime ： 2024/10/28 02:10
            @Author ：eblis
            @Motto：简单描述用途
        """
        # self.usego.sendlog(f"本次要删除 ：{len(links)} 条数据")
        query = {"url": {"$in": links}}
        sql_data = self.mossql.splicing_interim_delet("seo_external_links_post", query=query, multiple=True, clear_all=False)
        self.usego.sendlog(f"删除结果：{sql_data}")


    def post_to_wrapper(self, arts, postingStyle, user, this_res_list, link, bad_run_list, is_run_list, title_alt, alt_text):
        with threading.Lock():
            result = self.post_to_telegra(postingStyle, user, link, title_alt, alt_text, arts)
            if result:
                this_res_list.append(result)
                is_run_list.append(link)
                # alll_links_list.remove(link)
                # self.usego.sendlog(f"剩余：{len(alll_links_list)} 组需要执行")
                # self.del_run_links(link)

            else:
                self.usego.sendlog(f"执行失败了，{link} 这些需要回炉再造")
                bad_run_list.append(link)
                
                
    def siphon_adsuser(self, lst, group_size):
        """
            @Datetime ： 2024/10/28 01:42
            @Author ：eblis
            @Motto：简单描述用途
        """
        return [lst[i:i + group_size] for i in range(0, len(lst), group_size)]
    

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

    def post_to_telegra(self, postingStyle, adsUser, this_links, title_alt, alt_text, arts):
        # 生成标题
        this_title = f"""{title_alt}-{self.usego.redome_string("小写字母", 10, 20)}"""
        driver = None

        self.usego.sendlog(f"接收到的postingStyle: {type(postingStyle)},{postingStyle}")

        try:
            # 初始化浏览器驱动
            driver = self.ads.basicEncapsulation(adsUser, configCall.adsServer)

            try:
                driver.get("https://telegra.ph/")
            except Exception as e:
                self.usego.sendlog(f"driver.get 出现异常: {e}")
                return None

            # 等待页面元素加载
            wait = WebDriverWait(driver, 10)

            try:
                # 设置标题
                title_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/h1')))
                driver.execute_script("arguments[0].textContent = arguments[1];", title_input, this_title)
            except Exception as e:
                self.usego.sendlog(f"标题设置失败: {e}")
                return None

            try:
                # 设置内容输入框为空
                content_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/p')))
                driver.execute_script("arguments[0].textContent = '';", content_input)
            except Exception as e:
                self.usego.sendlog(f"内容输入框设置失败: {e}")
                return None

            # 如果有文章内容，则添加
            if arts:
                try:
                    driver.execute_script("""
                        var p = document.createElement('p');
                        p.textContent = arguments[0];
                        arguments[1].appendChild(p);
                    """, arts, content_input)
                except Exception as e:
                    self.usego.sendlog(f"添加文章内容失败: {e}")
                    return None

            # 根据 postingStyle 执行不同的链接处理
            if int(postingStyle) == 0:
                self.add_links_as_text(this_links, alt_text, content_input, driver)
            elif int(postingStyle) == 1:
                self.add_links_as_paragraph(this_links, content_input, driver)
            else:
                self.add_links_in_mixed_style(this_links, content_input, driver)

            # 发布文章
            try:
                publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_publish_button"]')))
                driver.execute_script("arguments[0].click();", publish_button)
            except Exception as e:
                self.usego.sendlog(f"点击发布按钮失败: {e}")
                return None

            # 随机等待一段时间
            time.sleep(self.usego.randomRandint(5, 10))
            return driver.current_url

        except Exception as e:
            self.usego.sendlog(f"页面操作失败: {e}")
            return None

        finally:
            # 结束后停止广告服务
            if driver:
                self.ads.adsAPI(configCall.adsServer, "stop", adsUser)

    def add_links_as_text(self, this_links, alt_text, content_input, driver):
        for link in this_links:
            link = link.strip('\n')
            try:
                driver.execute_script("""
                    var a = document.createElement('a');
                    a.href = arguments[0];
                    a.textContent = arguments[1];
                    a.target = '_blank';
                    arguments[2].appendChild(a);
                    arguments[2].appendChild(document.createTextNode('\u00A0'));
                """, link, alt_text, content_input)
            except Exception as e:
                self.usego.sendlog(f"添加链接失败: {e}")
                continue

    def add_links_as_paragraph(self, this_links, content_input, driver):
        for link in this_links:
            link = link.strip('\n')
            try:
                driver.execute_script("""
                    var p = document.createElement('p');
                    var a = document.createElement('a');
                    a.href = arguments[0];
                    a.textContent = arguments[0];
                    p.appendChild(a);
                    arguments[1].appendChild(p);
                """, link, content_input)
            except Exception as e:
                self.usego.sendlog(f"添加链接作为段落失败: {e}")
                continue

    def add_links_in_mixed_style(self, this_links, content_input, driver):
        for index, link in enumerate(this_links):
            link = link.strip('\n')
            try:
                if index < len(this_links) - 1:
                    driver.execute_script("""
                        var p = document.createElement('p');
                        p.textContent = arguments[0];
                        p.setAttribute('dir', 'auto');
                        arguments[1].appendChild(p);
                    """, link, content_input)
                else:
                    driver.execute_script("""
                        var p = document.createElement('p');
                        var a = document.createElement('a');
                        a.href = arguments[0];
                        a.target = '_blank';
                        a.textContent = arguments[0];
                        p.setAttribute('dir', 'auto');
                        p.appendChild(a);
                        arguments[1].appendChild(p);
                    """, link, content_input)
            except Exception as e:
                self.usego.sendlog(f"添加混合风格的链接失败: {e}")
                continue

    def save_res(self, urls):
        self.usego.sendlog(f"本次需要保存的数据有{len(urls)},{urls}")
        formatted_now = datetime.now().strftime("%Y%m%d")
        file_name = f"telegra_result_{formatted_now}.txt"
        today_file = self.usego.make_file(configCall.telegra_result, file_name)
        with open(today_file, 'a+') as f:
            for url in urls:
                f.write(f"{url}\n")
                
    def save_datebase(self, urls, genre, platform ):
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
    

if __name__ == '__main__':
    start_time = datetime.now()
    tele = telegraSelenium()
    # 调试，通过配置文件修改
    genre = "0"
    platform = "telegra"
    stacking_min = configCall.stacking_min
    stacking_max = configCall.stacking_max
    alt_text = configCall.stacking_text

    tele.main(genre, platform, stacking_min, stacking_max, alt_text, "1", "0", "1", "all", 0, 20)
