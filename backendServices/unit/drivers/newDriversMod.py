# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/7/5 13:52
@Author ： eblis
@File ：newDriversMod.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import publicFunctions.configuration as configuration

class NewDriversUtil:
    def drivers(self, debugUP=None, proxy=None, userAgent=None, userDataDir=None):

        """
        :service : from selenium.webdriver.chrome.service import Service 要使用selenium 4.1.0 以上
        :param driverpath:
                plugin_f: 插件存放路径
        :return:
        """

        option = self.chrome_options(debugUP, proxy, userAgent, userDataDir)

        # 创建一个 WebDriver 对象
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=option)

        driver.implicitly_wait(30)
        # driver.set_page_load_timeout(90)

        # wait = WebDriverWait.Chrome(driver, 10, 0.5)  # 显示等待，设置等待10秒，每0.5秒检查一次看页面加载出来没有。继续操作下面
        # driver = webdriver.Chrome(executable_path=driverpath)

        return driver

    def chrome_options(self, debugUP, proxy, userAgent, userDataDir):
        """定制的options让他看起来更像一个webapp页面"""

        # 创建一个 Options 对象
        options = Options()

        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')

        options.add_argument("--disable-blink-features=AutomationControlled")

        # 验证码插件
        options.add_extension(f"{configuration.ye_plug_in}")
        # 设置浏览器窗口大小为宽1200像素，高800像素
        # options.add_argument('--start-maximized')

        # 自动打开开发者工具
        # options.add_argument('--auto-open-devtools-for-tabs')

        if debugUP is not None:
            options.add_experimental_option("debuggerAddress", debugUP)


        if userAgent is not None:
            # configuration.userAgent
            options.add_argument(f"user-agent={userAgent}")

        if userDataDir is not None:
            options.add_argument(f"user-data-dir={userDataDir}")

        if proxy is not None:
            options.add_argument(f'--proxy-server={proxy}')

        return options