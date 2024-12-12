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
from middleware.deviceManage.elementUsage import component
from backendServices.src.awsMQ.amazonSQS import AmazonSQS


class bloggerSelenium:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()
        self.aws_sqs = AmazonSQS()

    def main(self, pcname, queue_url, genre, platform, stacking_min, stacking_max, title_alt,  alt_text, sort, isarts, postingStyle, group, start, end):
        """
            @Datetime ： 2024/10/26 00:09
            @Author ：eblis
            @Motto：简单描述用途
        """

        self.usego.sendlog(f"接收到的参数：genre{genre}, platform{platform}, stacking_min{stacking_min}, stacking_max{stacking_max},alt_text {alt_text},sort {sort}, postingStyle{postingStyle}, isarts{isarts}")
        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=1)
        adsUserlist = self.siphon_adsuser(group, eval(configCall.min_concurrent_user))

        if adsUserlist != []:
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

                    self.usego.sendlog(f"拆分为：{len(alll_links_list)} 组")

                    all_res = self.run(isarts, postingStyle, platform, genre, adsUserlist, alll_links_list, title_alt, alt_text)

                    sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
                    self.aws_sqs.deleteMSG(queue_url)
                    return all_res


        sql_data = self.ssql.pcSettings_update_state_sql(pcname, state=0)
        self.aws_sqs.deleteMSG(queue_url)

        return None


    def run (self, isarts, postingStyle, platform, genre, adsUserlist, alll_links_list,title_alt, alt_text):
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
            self.usego.sendlog(f"第 {mun} 执行开始,剩余{len(alll_links_list)-1} 组数据待处理")
            if len(adsUserlist) > mm:
                this_res_list = []
                bad_run_list = []
                threads = []
                this_group_ads = adsUserlist[mm]
                self.usego.sendlog(f"这组ads选手分别是{this_group_ads}")
                this_go = min(len(this_group_ads), len(alll_links_list))
                self.usego.sendlog(f"需要建立{this_go} 个 线程")
                for i in range(this_go):
                    if int(isarts) == 0:
                        arts = self.read_file()
                    else:
                        arts = None
                    user = self.usego.changeDict(this_group_ads[i])
                    link = alll_links_list[i]
                    self.usego.sendlog(f"这组 使用的是{user},发布的是{link} 链接")

                    t = threading.Thread(target=self.post_wrapper, args=(arts, postingStyle, this_res_list, link, alll_links_list, bad_run_list, user["bloggerID"], user["adsID"], title_alt, alt_text))

                    threads.append(t)
                    t.start()
                    time.sleep(3)

                for thread in threads:
                    thread.join()

                self.usego.sendlog(f"这波Thread 执行完了：{this_res_list}")

                self.save_res(this_res_list)

                if this_res_list !=[]:

                    self.usego.sendlog(f"将数据同步存放数据库")

                    self.usego.sendlog(f"{self.save_datebase(this_res_list, genre, platform)}")

                self.usego.sendlog(f"总剩余：{len(alll_links_list)}")

                alll_links_list.extend(bad_run_list)
                bad_run_list.clear()
                self.usego.sendlog(f"最终剩余：{len(alll_links_list)}")

                for link in this_res_list:
                    if link not in all_res:
                        all_res.append(link)

                mm = mm + 1
                mun = mun + 1

            else:
                self.usego.sendlog(f"{adsUserlist} 都跑过了")
                runTure = False
    
    def post_wrapper(self, arts, postingStyle, result_list, this_links, all_list, bad_run_list, bloggerID, adsUser,  title_alt, alt_text):
        """
            @Datetime ： 2024/11/2 13:26
            @Author ：eblis
            @Motto：简单描述用途
        """
        with threading.Lock():
            result = self.post_to_blogger(arts, postingStyle, bloggerID, adsUser, this_links, title_alt, alt_text)
            if result:
                if "git.html" not in result:
                    result_list.append(result)
                    all_list.remove(this_links)
                    self.usego.sendlog(f"剩余：{len(all_list)}")

                    self.del_run_links(this_links)
                else:
                    self.usego.sendlog(f"丢弃结果: {result}，因为它包含 'git.html'")
            else:
                bad_run_list.append(this_links)

    def post_to_blogger(self, arts, postingStyle, bloggerID, adsUser, this_links, title_alt, alt_text):
        try:
            # 输出接收到的参数
            self.usego.sendlog(f"接收到的postingStyle: {type(postingStyle)},{postingStyle}")
            # self.usego.sendlog(f"arts: {type(arts)},{arts}")

            # 获取文章内容链接
            all_atab = self.get_links(arts, postingStyle, this_links, alt_text)

            # 获取浏览器驱动
            driver = self.ads.basicEncapsulation(adsUser, configCall.adsServer)
            driver.get(f"https://www.blogger.com/blog/posts/{bloggerID}")
            time.sleep(3)

            # 初始化组件
            comp = component(driver)

            # 点击“New Post”
            self._click_new_post_button(comp, driver)

            # 输入标题
            self._input_title(comp, title_alt)

            # 进入HTML编辑模式
            self.usego.sendlog("进入html 编辑状态")
            time.sleep(15)

            # 输入内容
            self._input_content(driver, comp, all_atab)

            # 点击发布
            self._click_publish_button(comp, driver)

            # 确认弹窗
            self._handle_popup(comp, driver)

            # 获取发布后的链接
            atag = self._get_publish_link(comp)
            time.sleep(10)

            self.ads.adsAPI(configCall.adsServer, "stop", adsUser)

            return atag

        except Exception as e:
            self.usego.sendlog(f"出错了: {str(e)}")
            self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
            return False

    def _click_new_post_button(self, comp, driver):
        try:
            new_post_button = comp.find_ele((By.XPATH, "//span[text()='New Post']"))
            if new_post_button:
                self.usego.sendlog("能识别到New Post")
                driver.execute_script("arguments[0].click();", new_post_button)
            else:
                new_post_button = comp.find_ele((By.XPATH,
                                                 '''//*[@id="yDmH0d"]/c-wiz/div[1]/gm-raised-drawer/div/div[2]/div/c-wiz/div[3]/div/div/span/span'''))
                driver.execute_script("arguments[0].click();", new_post_button)
            time.sleep(10)
        except Exception as e:
            self.usego.sendlog(f"点击New Post时发生错误: {str(e)}")
            raise

    def _input_title(self, comp, alt_text):
        try:
            title_input = comp.input(
                (By.XPATH, '''//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[1]/div[1]/div[1]/div/div[1]/input'''),
                alt_text)
            self.usego.sendlog("标题输入了，下一步")
        except Exception as e:
            self.usego.sendlog(f"输入标题时发生错误: {str(e)}")
            raise

    def _input_content(self, driver, comp, all_atab):
        try:
            # 等待目标元素的加载
            content_xpath = '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[2]/div/div/div[3]/span/div/div[2]/div[2]/div/div/div'
            content_ele = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, content_xpath))
            )

            # 将 JavaScript 操作合并
            driver.execute_script("""
                const contentElement = arguments[0];
                if (contentElement && contentElement.CodeMirror) {
                    contentElement.focus();
                    contentElement.CodeMirror.setValue(arguments[1]);
                } else {
                    throw new Error("CodeMirror editor not found or not initialized.");
                }
            """, content_ele, all_atab)

        except Exception as e:
            self.usego.sendlog(f"输入内容时发生错误: {str(e)}")
            raise

    def _click_publish_button(self, comp, driver):
        time.sleep(15)
        try:
            publish_button = comp.find_ele(
                (By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[1]/div[2]/div[4]/span/span/div/div'))
            driver.execute_script("arguments[0].click();", publish_button)
        except Exception as e:
            self.usego.sendlog(f"点击发布按钮时发生错误: {str(e)}")
            raise

    def _handle_popup(self, comp, driver):
        try:
            pop_up = comp.find_ele((By.XPATH, '''//*[@id="dwrFZd0"]'''))
            if pop_up:
                confirm_button = comp.find_ele((By.XPATH, '//*[@id="yDmH0d"]/div[4]/div/div[2]/div[3]/div[2]'))
                self.usego.sendlog(f"confirm_button: {confirm_button}")
                driver.execute_script("arguments[0].click();", confirm_button)
        except Exception as e:
            self.usego.sendlog(f"处理弹窗时发生错误: {str(e)}")
            raise

    def _get_publish_link(self, comp):
        try:
            atag = comp.get_element_attribute(
                (By.XPATH,
                 '//*[@id="yDmH0d"]/c-wiz/div[2]/div/c-wiz/div[2]/c-wiz/div/div/div/div[1]/div/span/div/div/div[3]/div[4]/div/a'),
                "href"
            )
            self.usego.sendlog(f"atag结果：{atag}")
            return atag
        except Exception as e:
            self.usego.sendlog(f"获取发布链接时发生错误: {str(e)}")
            raise

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


    def siphon_adsuser(self, group, group_size):
        """
            @Datetime ： 2024/10/28 01:42
            @Author ：eblis
            @Motto：简单描述用途
        """
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
        # self.usego.sendlog(f"本次要删除 ：{len(links)} 条数据")
        query = {"url": {"$in": links}}
        sql_data = self.mossql.splicing_interim_delet("seo_external_links_post", query=query, multiple=True,
                                                      clear_all=False)
        self.usego.sendlog(f"删除结果：{sql_data}")


    def save_res(self, urls):
        self.usego.sendlog(f"本次需要保存的数据有{len(urls)},{urls}")
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
        create_at = now.strftime("%Y-%m-%d %H:%M:%S")
        new_links_list = []
        for url in urls:
            this_dat = {
                "url": f"{url}",
                "platform": f"{platform}",
                "genre": f"{genre}",
                "create_at": create_at
            }
            new_links_list.append(this_dat)
        result = self.mossql.splicing_interim_insert_batch("seo_result_301_links", new_links_list)
        if result is not None:  # 修改这里，检查 result 是否为 None
            return f"生成 {len(new_links_list)} 个新链接，已入库"
        else:
            return None


if __name__ == '__main__':
    blog = bloggerSelenium()
    # 调试，通过配置文件修改
    # genre = "0"
    # platform = "blogger"
    # stacking_min = configCall.stacking_min
    # stacking_max = configCall.stacking_max
    # alt_text = configCall.stacking_text
    # start = 0
    # end = 2000
    # group = "all"
    # blog.main(genre, platform, stacking_min, stacking_max, alt_text, group, start, end)
    this_links = ["https://udl.forem.com/?r=https://www.aitomitsu.com/how-much-is-camel-coffee/","https://udl.forem.com/?r=https://www.awayaicchou.com/what-will-become-of-zozotown-stock-prices/ ","https://udl.forem.com/?r=https://www.awayaicchou.com/what-will-be-the-price-of-japan-elevator/"]
    alt_text = "听雨闻花香"
    title_alt = "听雨闻花香"

    blog.post_to_blogger(None, 0, "4348553235008786550", "klak6lr", this_links, title_alt,  alt_text)





