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

class telegraSeleniumGO:
    def __init__(self):
        self.usego = otherUse()
        self.ads = adsDevice()


    def run(self, adsUser, title, content):
        # 生成标题
        driver = None
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
                driver.execute_script("arguments[0].textContent = arguments[1];", title_input, title)
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
            # 输入内容
            self.usego.sendlog(f"输入内容")
            html_tab = ["<h2>", "<h3>", "<p>"]
            try:
                # 检查是否包含特定的 HTML 标签
                if any(tag in content for tag in html_tab):
                    self.usego.sendlog("检测到特定 HTML 标签，使用 div 包裹插入内容")
                    driver.execute_script("""
                        var content = arguments[0];
                        var contentInput = arguments[1];
                        var div = document.createElement('div');
                        div.innerHTML = content;  // 插入 HTML 内容
                        contentInput.appendChild(div);
                    """, content, content_input)
                else:
                    self.usego.sendlog("未检测到 HTML 标签，作为纯文本插入")
                    driver.execute_script("""
                        var p = document.createElement('p');
                        p.textContent = arguments[0];  // 插入纯文本
                        arguments[1].appendChild(p);
                    """, content, content_input)
            except Exception as e:
                self.usego.sendlog(f"添加文章内容失败: {e}")
                return None


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

            if driver:
                self.ads.adsAPI(configCall.adsServer, "stop", adsUser)
                
    def changeText(self, content):
        """
            @Datetime ： 2024/12/4 20:03
            @Author ：eblis
            @Motto：简单描述用途
        """


    



    

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
