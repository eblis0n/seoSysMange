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

class telegraSelenium:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()
        self.mossql = mongo_sqlGO()


    def main(self, genre, platform, stacking_min, stacking_max, alt_text):
        """
            @Datetime ： 2024/10/26 00:09
            @Author ：eblis
            @Motto：简单描述用途
        """

        sql_data = self.mossql.telegra_interim_findAll("seo_external_links_post", genre=str(genre),
                                       platform=str(platform), limit=200000)


        if sql_data is not None:
            all_links = [data["url"] for data in sql_data] if sql_data else []

            if all_links:
                all_res = self.run(all_links, stacking_min, stacking_max, alt_text)
                query = {"url": {"$in": all_res}}
                sql_data = self.mossql.telegra_interim_multiple_delet("seo_external_links_post", query)
                self.usego.sendlog(f"删除结果：{sql_data}")

                return all_res
        return None





    def run(self, all_links, stacking_min, stacking_max, alt_text):
        all_res = []

        alll_links_list = self.siphon_links(all_links, stacking_min, stacking_max)
        bad_run_list = []
        adsUser = eval(configCall.telegra_ads)
        minadsUser = eval(configCall.min_concurrent_user)
        num_users = len(adsUser)
        user_index = 0
        mun = 0

        while alll_links_list:
            self.usego.sendlog(f"第 {mun} 执行开始")
            res_list = []
            threads = []
            this_go = min(minadsUser, len(alll_links_list))

            for i in range(this_go):

                user = adsUser[user_index % num_users]
                link = alll_links_list[i]
                t = threading.Thread(target=self.post_to_telegraph_wrapper,
                                     args=(user, res_list, link, alll_links_list, bad_run_list, alt_text))
                user_index += 1
                threads.append(t)
                t.start()
                time.sleep(3)

            for thread in threads:
                thread.join()
            self.usego.sendlog(f"这波Thread 执行完了：{res_list}")

            alll_links_list = alll_links_list[int(this_go):]
            self.save_res(res_list)

            self.save_datebase(res_list, genre, platform)

            alll_links_list.extend(bad_run_list)
            bad_run_list.clear()

            all_res.extend([item for item in res_list if item not in all_res])
            mun = mun + 1

        return all_res

    def post_to_telegraph_wrapper(self, user, result_list, link, all_list, bad_run_list, alt_text):
        with threading.Lock():
            result = self.post_to_telegraph(user, link, alt_text)
            if result:
                result_list.append(result)
                all_list.remove(link)
            else:
                bad_run_list.append(link)

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

    def post_to_telegraph(self, adsUser, this_links, alt_text):
        this_title = self.usego.redome_string("小写字母", 10, 20)
        driver = None
        try:
            driver = self.ads.basicEncapsulation(adsUser, configCall.adsServer)
            driver.get("https://telegra.ph/")
            wait = WebDriverWait(driver, 5)

            title_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/h1')))
            driver.execute_script("arguments[0].textContent = arguments[1];", title_input, this_title)

            content_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/p')))
            driver.execute_script("arguments[0].textContent = '';", content_input)

            for link in this_links:
                link = link.strip('\n')
                driver.execute_script("""
                    var a = document.createElement('a');
                    a.href = arguments[0];
                    a.textContent = arguments[1];
                    a.target = '_blank';
                    arguments[2].appendChild(a);
                    arguments[2].appendChild(document.createTextNode('\u00A0'));
                """, link, alt_text, content_input)

            publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_publish_button"]')))
            driver.execute_script("arguments[0].click();", publish_button)

            time.sleep(self.usego.randomRandint(10, 15))
            return driver.current_url

        except Exception as e:
            self.usego.sendlog(f"Error in post_to_telegraph: {e}")
            return None
        finally:
            if driver:
                self.ads.adsAPI(configCall.adsServer, "stop", adsUser)

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
                    "platform": platform,
                    "genre": genre,
                    "created_at": created_at
                }
            new_links_list.append(this_dat)
        result = self.mossql.telegra_interim_insert_batch("seo_result_301_links", new_links_list)
        if result is not None:  # 修改这里，检查 result 是否为 None
            return f"生成 {len(new_links_list)} 个新链接，已入库"
        else:
            return None
    

if __name__ == '__main__':
    start_time = datetime.now()
    tele = telegraSelenium()
    mossql = mongo_sqlGO()
    genre = "0"
    platform = "telegra"
    sql_data = mossql.telegra_interim_findAll("seo_external_links_post", genre=genre,
                                                   platform=platform, limit=100000)


