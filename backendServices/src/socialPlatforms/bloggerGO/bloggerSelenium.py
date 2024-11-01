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
from middleware.deviceManage.elementUsage import component


class bloggerSelenium:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()
        self.mossql = mongo_sqlGO()


    def main(self, genre, platform, stacking_min, stacking_max, alt_text, start, end):
        """
            @Datetime ： 2024/10/26 00:09
            @Author ：eblis
            @Motto：简单描述用途
        """
        adsUserlist = self.siphon_adsuser(eval(configCall.stacking_ads), eval(configCall.min_concurrent_user))

        sql_data = self.mossql.splicing_interim_findAll("seo_external_links_post", genre=str(genre),
                                       platform=str(platform), start=int(start), end=int(end))


        if sql_data is not None:
            all_links = [data["url"] for data in sql_data] if sql_data else []

            if all_links:
                alll_links_list = self.siphon_links(all_links, stacking_min, stacking_max)

                self.usego.sendlog(f"拆分为：{len(alll_links_list)} 组")

                all_res = self.run(platform, genre, adsUserlist, alll_links_list,  alt_text)

                return all_res

        return None
    

    def run (self, platform, genre, adsUserlist, alll_links_list, alt_text):
        all_res = []
        mun = 0
        mm = 0
        while len(alll_links_list) > 0:
            self.usego.sendlog(f"第 {mun} 执行开始,剩余{len(alll_links_list)} 组数据待处理")
            if len(adsUserlist) > mm:
                res_list = []
                threads = []
                bad_run_list = []
                thisnoneads = adsUserlist[mm]
                self.usego.sendlog(f"这组ads选手分别是{thisnoneads}")
                this_go = min(len(thisnoneads), len(alll_links_list))
                self.usego.sendlog(f"需要建立{this_go} 个 线程")
                for i in range(this_go):
                    user = thisnoneads[i]
                    link = alll_links_list[i]
                    self.usego.sendlog(f"这组 使用的是{user},发布的是{link} 链接")
                    t = threading.Thread(target=self.post_to_telegraph_wrapper,
                                         args=(user, res_list, link, alll_links_list, bad_run_list, alt_text))

                    threads.append(t)
                    t.start()
                    time.sleep(3)

                for thread in threads:
                    thread.join()

                self.usego.sendlog(f"这波Thread 执行完了：{res_list}")

                self.save_res(res_list)

                self.usego.sendlog(f"将数据同步存放数据库")

                self.usego.sendlog(f"{self.save_datebase(res_list, genre, platform)}")
                self.usego.sendlog(f"总剩余：{len(alll_links_list)}")

                alll_links_list.extend(bad_run_list)
                bad_run_list.clear()
                self.usego.sendlog(f"最终剩余：{len(alll_links_list)}")

                for link in res_list:
                    if link not in all_res:

                        all_res.append(link)

                mm = mm + 1
                mun = mun + 1
            else:
                self.usego.sendlog(f"初始化一下数据，跑空")
                mm = 0


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


    def post_to_telegraph_wrapper(self, bloggerID, user, result_list, link, all_list, bad_run_list, alt_text):
        with threading.Lock():
            result = self.post_to_blogger(bloggerID, user, link, alt_text)
            if result:
                result_list.append(result)
                all_list.remove(link)
                self.usego.sendlog(f"剩余：{len(all_list)}")

                self.del_run_links(link)

            else:
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

    def post_to_blogger(self, bloggerID, adsUser, this_links, alt_text):
        # this_title = self.usego.redome_string("小写字母", 10, 20)

        driver = self.ads.basicEncapsulation(adsUser, configCall.adsServer)
        driver.get(f"https://www.blogger.com/blog/posts/{bloggerID}")
        # wait = WebDriverWait(driver, 5)
        comp = component(driver)

        time.sleep(3)


        # 点击发帖
        new_post_bottom = comp.find_ele((By.XPATH, "//span[text()='New Post']"))
        driver.execute_script("arguments[0].click();", new_post_bottom)
        time.sleep(5)
        # 找到 标题元素并输入
        title_input = comp.input((By.XPATH, '''//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[1]/div[1]/div[1]/div/div[1]/input'''),alt_text)
        print("标题输入了，下一步")

        time.sleep(1)
        #
        # menu_bottom = comp.find_ele((By.XPATH,'''//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]'''))
        #
        # if menu_bottom:
        #     driver.execute_script("arguments[0].click();", menu_bottom)
        #
        # print("点击了富文本菜单列表")
        #
        # html_ele = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/span'))
        # print("html_ele", html_ele)
        #
        # if html_ele:
        #     try:
        #         html_ele.click()
        #     except:
        #         driver.execute_script("arguments[0].click();", html_ele)
        # time.sleep(1)
        # driver.execute_script("arguments[0].click();", menu_bottom)
        #
        # pen_ele = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/span'))
        # print("pen_ele", pen_ele)
        #
        # if pen_ele:
        #     try:
        #         pen_ele.click()
        #     except:
        #         driver.execute_script("arguments[0].click();", pen_ele)
        # time.sleep(5)
        # pen_bottom = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[1]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[2]/div[2]/span'))
        # print("pen_bottom",pen_bottom)
        # try:
        #     pen_bottom.click()
        # except:
        #     driver.execute_script("arguments[0].click();", pen_bottom)
        #
        # time.sleep(5)
        # html_ele1 = comp.find_ele((By.XPATH,
        #                           '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[1]/div[1]/div[1]/div[1]/div/div[2]/div[1]/span'))
        # print("html_ele1", html_ele1)
        # if html_ele1:
        #     try:
        #         html_ele1.click()
        #     except:
        #         driver.execute_script("arguments[0].click();", html_ele1)


        print("进入html 编辑状态")


        conent_ele = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[2]/div[2]/div/div/div'))
    #

        all_atab = self.get_links(this_links, alt_text)
        driver.execute_script("arguments[0].focus();", conent_ele)

        driver.execute_script(f"arguments[0].CodeMirror.setValue('{all_atab}');", conent_ele)

        #
        time.sleep(5)
        publish_button = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[1]/div[2]/div[@data-tooltip="Publish"]/span'))

        driver.execute_script("arguments[0].click();", publish_button)

        pop_up = comp.find_ele((By.XPATH, "//div[text()='Publish post?']"))

        if pop_up:

            confirm_button = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/div[4]/div/div[2]/div[3]/div[2]'))
            print("confirm_button", confirm_button)

            try:
                driver.execute_script("arguments[0].click();", confirm_button)
            except:
                print("使用 click")
                confirm_button.click()

        time.sleep(10)

        atag = comp.get_element_attribute((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[2]/div/c-wiz/div[2]/c-wiz/div/div/div/div[1]/div/span/div/div/div[3]/div[4]/div/a'), "href")
        print("atag",atag)
        self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
        return atag


    def get_links(self,this_links, alt_text):
        """
            @Datetime ： 2024/10/30 16:56
            @Author ：eblis
            @Motto：简单描述用途
        """
        all_atab = ''
        for link in this_links:
            self.usego.sendlog(f"这条连接是：{link}")
            link = link.strip('\n')
            this_atab = f"""<a href="{link}" target="_blank">{alt_text}</a>&nbsp;"""
            all_atab += this_atab
        print("all_atab", all_atab)
        return all_atab


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
    # start_time = datetime.now()
    blog = bloggerSelenium()
    # 调试，通过配置文件修改
    genre = "0"
    platform = "telegra"
    stacking_min = configCall.stacking_min
    stacking_max = configCall.stacking_max
    alt_text = configCall.stacking_text
    blog.main(genre, platform, stacking_min, stacking_max, alt_text)
    # bloggerID ="3691937055035842433"
    # adsUser = "j4tkc0y"
    # this_links = ["https://padlet.com/redirect?url=https://www.4shared.com/u/NNIxS1ee/partlenportte1982.html","https://padlet.com/redirect?url=https://www.4shared.com/u/ca2gJQWr/lucestisu1980.html","https://padlet.com/redirect?url=https://www.4shared.com/u/LDmYjCBR/nettbullcumto1975.html","https://padlet.com/redirect?url=https://www.4shared.com/u/NNIxS1ee/partlenportte1982.html","https://padlet.com/redirect?url=https://www.4shared.com/u/ca2gJQWr/lucestisu1980.html","https://padlet.com/redirect?url=https://www.4shared.com/u/LDmYjCBR/nettbullcumto1975.html","https://padlet.com/redirect?url=https://www.4shared.com/u/NNIxS1ee/partlenportte1982.html","https://padlet.com/redirect?url=https://www.4shared.com/u/ca2gJQWr/lucestisu1980.html","https://padlet.com/redirect?url=https://www.4shared.com/u/LDmYjCBR/nettbullcumto1975.html","https://padlet.com/redirect?url=https://www.4shared.com/u/NNIxS1ee/partlenportte1982.html","https://padlet.com/redirect?url=https://www.4shared.com/u/ca2gJQWr/lucestisu1980.html","https://padlet.com/redirect?url=https://www.4shared.com/u/LDmYjCBR/nettbullcumto1975.html","https://padlet.com/redirect?url=https://www.4shared.com/u/NNIxS1ee/partlenportte1982.html","https://padlet.com/redirect?url=https://www.4shared.com/u/ca2gJQWr/lucestisu1980.html","https://padlet.com/redirect?url=https://www.4shared.com/u/LDmYjCBR/nettbullcumto1975.html","https://padlet.com/redirect?url=https://www.4shared.com/u/NNIxS1ee/partlenportte1982.html","https://padlet.com/redirect?url=https://www.4shared.com/u/ca2gJQWr/lucestisu1980.html","https://padlet.com/redirect?url=https://www.4shared.com/u/LDmYjCBR/nettbullcumto1975.html"]
    # alt_text = "学习知识"
    # title = "可进一步学习相关知识"
    # blog.post_to_blogger(bloggerID, adsUser, this_links, alt_text)