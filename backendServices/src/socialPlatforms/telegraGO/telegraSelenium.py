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

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.deviceManage.adsDevice import adsDevice
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading


class telegraSelenium():

    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()
        self.mossql = mongo_sqlGO()



    def run(self, all_links, stacking_min, stacking_max, alt_tex):
        """
            @Datetime ： 2024/10/17 19:17
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"开始")
        all_res_list = []
        alll_links_list = self.siphon_links(all_links, stacking_min, stacking_max)
        bad_run_list = []
        adsUser = eval(configCall.telegra_ads)
        minadsUser = eval(configCall.min_concurrent_user)
        num_users = len(adsUser)
        num_links = len(alll_links_list)
        user_index = 0  # 用户轮询索引


        # 每次从 adsUser 拿 10 个出来跑
        while len(alll_links_list) > 0:
            res_list = []
            print(f"剩余 {len(alll_links_list)} 需要执行！！")

            threads = []  # 清空上一轮线程
            # 每次最多取 10 个用户和对应的 10 个链接组
            this_go = min(minadsUser, num_links)
            for i in range(this_go):  # 最多取 10 个任务，防止越界
                # 使用 user_index 确保轮询 adsUser
                user = adsUser[user_index % num_users]
                link = alll_links_list[i]

                t = threading.Thread(target=self.post_to_telegraph_wrapper,
                                     args=(user, res_list, link, alll_links_list, bad_run_list, alt_tex,))
                user_index += 1  # 移动到下一个用户
                threads.append(t)
                t.start()
                time.sleep(3)  # 每个线程启动时延迟 3 秒
            print("这波线程准备就绪！")
            # 等待所有线程完成
            for thread in threads:
                thread.join()

            alll_links_list = alll_links_list[10:]  # 每次移除前 10 个处理过的链接

            print(f"这波跑完了，这是成功的：{res_list},bad_run_list 记录结果{bad_run_list}")
            self.save_res(res_list)
            if bad_run_list !=[]:
                for bad in bad_run_list:
                    alll_links_list.append(bad)


            num_links = len(alll_links_list)  # 更新剩余的链接数量



            all_res_list.extend([item for item in res_list if item not in all_res_list])  # 第一次添加

        
        return all_res_list
    


    # 线程函数，执行 post 并将结果写入 res_list，同时从 this_go_list 删除已处理的 link
    def post_to_telegraph_wrapper(self, user, result_list, link, all_list, bad_run_list, alt_tex):
        # 使用线程锁确保线程安全
        lock = threading.Lock()
        result = tele.post_to_telegraph(user, link, alt_tex)  # 执行发布操作

        # 如果结果不是 None，则写入 res_list，并从 this_go_list 删除 link
        if result is not None:
            with lock:  # 确保线程安全
                result_list.append(result)  # 将结果写入 res_list
                all_list.remove(link)  # 从 this_go_list 删除已处理的 link
        else:
            bad_run_list.append(link)



    def siphon_links(self, all_links, rmin, rmax):
        """
            @Datetime ： 2024/10/16 16:32
            @Author ：eblis
            @Motto：简单描述用途
        """

        # 第一步：将 连接划分
        this_run_list = []
        # with open(config.telegra_301_file, 'r', encoding='utf-8') as f:
        #     all_links = f.readlines()

        allLinks = [item for item in all_links if item != '\n']

        while len(allLinks) > 0:
            num_links_to_add = min(len(allLinks), self.usego.randomRandint(int(rmin), int(rmax)))
            selected_links = self.usego.redome_sample(allLinks, num_links_to_add)
            print(f"把本次使用{len(selected_links)} 连接")
            this_run_list.append(selected_links)
            for link in selected_links:
                allLinks.remove(link)

        print(f"一共有{len(this_run_list)} 组需要执行")
        return this_run_list



    def post_to_telegraph(self, adsUser, this_links, alt_tex):


        this_title = self.usego.redome_string("小写字母", 10, 20)

        driver = self.ads.basicEncapsulation(adsUser, configCall.adsServer)
        time.sleep(10)

        # 打开网页
        print("开始...")
        try:
            driver.get("https://telegra.ph/")
        except:
            self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
            return None
        # 等待并找到标题的输入框
        # print("Waiting for title input to be clickable...")
        wait = WebDriverWait(driver, 5)
        try:
            title_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/h1')))
            # print("Title input is clickable")

        except:
            self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
            return None
        else:
            print(f"Setting title: {this_title}")
            driver.execute_script("arguments[0].textContent = arguments[1];", title_input, this_title)

            time.sleep(5)
            # print("Waiting for content input to be clickable...")
            # 填充内容部分
            try:
                content_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/p')))

                # 清除内容输入框的现有内容
                driver.execute_script("arguments[0].textContent = '';", content_input)
            except:

                self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
                return None
            else:
                print("this_links:", len(this_links), this_links)
                # 插入链接
                for link in this_links:
                    link = link.strip('\n')
                    # driver.execute_script("""
                    #     var a = document.createElement('a');
                    #     a.href = arguments[0];
                    #     a.textContent = arguments[1];
                    #     arguments[2].appendChild(a);
                    #     var space = document.createTextNode('\u00A0');
                    #     arguments[2].appendChild(space);
                    # """, link, alt_tex, content_input)
                    driver.execute_script("""
                        var a = document.createElement('a');
                        a.href = arguments[0];  // 链接地址
                        a.textContent = arguments[1];  // 链接文字
                        a.target = '_blank';  // 打开新标签页
                        arguments[2].appendChild(a);

                        // 添加空格
                        var space = document.createTextNode('\u00A0');
                        arguments[2].appendChild(space);
                    """, link, alt_tex, content_input)

                time.sleep(3)

                # 发布
                print("发布中...")
                try:
                    publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_publish_button"]')))
                    driver.execute_script("arguments[0].click();", publish_button)
                    # print("Publish button is clickable")
                except:
                    self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
                    return None
                else:
                    # 等待几秒钟
                    time.sleep(self.usego.randomRandint(10, 15))
                    # 获取发布后的链接

                    published_url = driver.current_url
                    print(f"Published URL: {published_url}")
                    self.ads.adsAPI(configCall.adsServer, "stop", adsUser)

                    return published_url



    def save_res(self, urls):
        """
            @Datetime ： 2024/10/17 19:45
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 获取当前日期和时间
        now = datetime.now()
        # 格式化日期和时间
        formatted_now = now.strftime("%Y%m%d")
        file_name = f"telegra_result_{formatted_now}.txt"
        today_file = self.usego.make_file(configCall.telegra_result, file_name)
        with open(today_file, 'a+') as f:
            for url in urls:
                f.write(f"{url}\n")



if __name__ == '__main__':
    # 记录开始时间
    start_time = datetime.now()
    tele = telegraSelenium()
    mossql = mongo_sqlGO()
    sql_data = mossql.telegra_interim_find_max("seo_external_links_post", max=100000)


    all_links = []
    if sql_data != []:
        for data in sql_data:
            all_links.append(data["url"])
        print(f"{len(all_links)}")

        tele.run(all_links, configCall.stacking_min, configCall.stacking_max, configCall.stacking_text)
        query = {"url": {"$in": all_links}}
        sql_data = mossql.telegra_interim_multiple_delet("seo_external_links_post", query)
        print(f"删除结果：{sql_data}")


        end_time = datetime.now()
        # 计算耗时
        execution_time = (end_time - start_time).total_seconds()
        print(f"代码执行耗时: {execution_time:.5f} 秒")
    else:
        print("没有可执行的数据")


