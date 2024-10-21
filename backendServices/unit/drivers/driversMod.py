# -*- coding: utf-8 -*-
"""
@Datetime ： 2023/11/9 14:57
@Author ： eblis
@File ：driversMod.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import publicFunctions.configuration as configuration


class DriversUtil:

    def drivers(self, driverpath, debugUP=None, proxy=None, userAgent=None, userDataDir=None):

        """
        :service : from selenium.webdriver.chrome.service import Service 要使用selenium 4.1.0 以上
        :param driverpath:
                plugin_f: 插件存放路径
        :return:
        """

        option = self.chrome_options(debugUP, proxy, userAgent, userDataDir)

        driverP = Service(r"{}".format(driverpath))

        driver = webdriver.Chrome(options=option, service=driverP)

        driver.implicitly_wait(30)


        # wait = WebDriverWait.Chrome(driver, 10, 0.5)  # 显示等待，设置等待10秒，每0.5秒检查一次看页面加载出来没有。继续操作下面
        # driver = webdriver.Chrome(executable_path=driverpath)

        return driver

    def chrome_options(self, debugUP,  proxy, userAgent, userDataDir):
        """定制的options让他看起来更像一个webapp页面"""

        options = webdriver.ChromeOptions()

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

    def stop(self, driverpath, debugUP=None):
        """
            @Datetime ： 2024/6/15 15:02
            @Author ：eblis
            @Motto：简单描述用途
        """
        driver = self.drivers(driverpath, debugUP)
        driver.quit()
        return True










