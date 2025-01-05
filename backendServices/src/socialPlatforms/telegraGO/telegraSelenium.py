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


class telegraSelenium:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()


    def run(self, adsUser,title_alt, postingStyle, this_links, alt_text, arts):
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


    

if __name__ == '__main__':
    pass
    # start_time = datetime.now()
    # tele = telegraSelenium()
    # # 调试，通过配置文件修改
    # genre = "0"
    # platform = "telegra"
    # stacking_min = configCall.stacking_min
    # stacking_max = configCall.stacking_max
    # alt_text = configCall.stacking_text
    #
    # tele.main(genre, platform, stacking_min, stacking_max, alt_text, "1", "0", "1", "all", 0, 20)
