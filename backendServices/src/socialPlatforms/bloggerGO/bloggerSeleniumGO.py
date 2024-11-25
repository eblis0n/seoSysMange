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
from middleware.deviceManage.elementUsage import component



class bloggerSeleniumGO:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()




    def run(self, bloggerID, adsUser, title_alt, content):
        try:
            # 输出接收到的参数
            # self.usego.sendlog(f"接收到的postingStyle: {type(postingStyle)},{postingStyle}")
            # self.usego.sendlog(f"arts: {type(arts)},{arts}")

            # 获取文章内容链接
            # all_atab = self.get_links(arts, postingStyle, this_links, alt_text)

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
            self._input_content(driver, comp, content)

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

    def _input_content(self, driver, comp, content):
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
            """, content_ele, content)

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


if __name__ == '__main__':
    blog = bloggerSeleniumGO()
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

    blog.run(None, 0, "4348553235008786550", "klak6lr", this_links, title_alt,  alt_text)





