# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/29 15:51
@Author ： eblis
@File ：elementUsage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import time

from twisted.conch.telnet import EC

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


import ast
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as when
from selenium.webdriver import ActionChains, Keys
from middleware.public.commonUse import otherUse


class basis(object):
    def __init__(self, driver):
        self.usego = otherUse()
        self.driver =driver
####################################################################### window ####################################################################################

class windows(basis):
    def all_window_handles(self):
        # 获取打开的多个窗口句柄
        handles = self.driver.window_handles
        return handles

    def this_window_handles(self):
        # 获取当前活动窗口的句柄
        current_handle = self.driver.current_window_handle
        return current_handle

    def assignation_window(self, handle):
        # 使用句柄切换到指定窗口
        self.driver.switch_to.window(handle)

    def open_window(self, url):
        # 新增标签页
        js = "window.open({},'_blank');".format(url)  # 打开新标签页
        self.driver.execute_script(js)

    def switch_to_default(self):
        """ iframe 切回主页面 """
        self.driver.switch_to.default_content()

    def switch_to_iframe(self, locator):
        try:
            # 定位 iframe
            iframe_element = self.driver.find_element(*locator)
            print("iframe_element",iframe_element)
            # 切换到 iframe
            self.driver.switch_to.frame(iframe_element)
        except Exception as e:
            print(f"切换到 iframe 失败: {e}")


######################################################################## ActionChains ####################################################################################

class actionGO(basis):

    def __init__(self, driver):
        super(actionGO, self).__init__(driver)
        self.action = ActionChains(self.driver)

    def move_by_offset_click(self, x1, y1):
        '''x坐标为正数向右偏移，x坐标为负数向左偏移'''
        '''y坐标为正数向下偏移，y坐标为负数向上偏移'''

        return self.action.move_by_offset(x1, y1).click().perform()

    def move_to(self, locator):
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        obj = wait.until(lambda x: x.find_element(*locator))
        return self.action.move_to_element(obj).perform()

    def perform_on(self):
        self.action.perform()

    def click(self, locator):
        """ 点击 """
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        obj = wait.until(lambda x: x.find_element(*locator))
        # 点击元素
        return self.action.click(obj).perform()

    def double_click(self, locator):
        """ 双击 """
        # 设置显性等待时间
        wait = WebDriverWait(self.driver, timeout=10)
        # 等待某个元素出现并可点击
        condition = when.element_to_be_clickable(*locator)
        # 定位元素.点击按钮
        element = wait.until(condition)
        # 双击元素
        return self.action.double_click(element).perform()

    def drag_and_drop(self, locator1, locator2):
        """ 拖动 """
        # 设置显性等待时间
        wait = WebDriverWait(self.driver, timeout=10)
        condition = when.element_to_be_clickable(locator1)
        element1 = wait.until(condition)
        # 定位到元素1，定位到元素2
        condition = when.element_to_be_clickable(locator2)
        element2 = wait.until(condition)
        # 拖动元素
        return self.action.drag_and_drop(element1, element2).perform()

    def emter(self):
        """ 回车 """
        return self.action.send_keys(Keys.ENTER).perform()

    def copy(self):
        """ 复制快捷键 """
        return self.action.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()

    def paste(self):
        """ 粘贴的快捷键 """
        return self.action.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

    def slide(self, locator, x, y):
        return self.action.click_and_hold(locator).move_by_offset(x, y).release().perform()


######################################################################## component ####################################################################################

class component(basis):

    def goto(self, url):
        """ 去哪个url地址 """
        return self.driver.get(url)

    def to_be_clickable(self, locator):
        """
            @Datetime ： 2024/10/29 16:12
            @Author ：eblis
            @Motto：简单描述用途
        """
        wait = WebDriverWait(self.driver, timeout=20)
        try:
            obj = wait.until(when.element_to_be_clickable(locator))
            return obj
        except Exception as e:
            print(f"element_to_be_clickable,输入内容元素无法定位{e}")
            return False

    def find_ele(self, locator):

        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            obj = wait.until(lambda x: x.find_element(*locator))
        except Exception as e:
            print(f"find_ele,查找元素失败{e}")
            return False
        else:
            print("find_ele，找到了元素")
            return obj

    def element_located(self, locator):
        """
            @Datetime ： 2024/10/30 20:23
            @Author ：eblis
            @Motto：简单描述用途
        """
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            # 使用 expected_conditions 来等待元素的可见性
            obj = wait.until(EC.presence_of_element_located(locator))  # 或者使用 EC.visibility_of_element_located(locator)
        except Exception as e:
            print(f"find_ele, 查找元素失败: {e}")
            return False
        else:
            print("find_ele，找到了元素")
            return obj

    def element_is_visible(self, locator):
        """
            @Datetime ： 2024/10/30 20:23
            @Author ：eblis
            @Motto：等待元素可见并返回该元素
        """
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            # 等待元素的可见性
            obj = wait.until(EC.visibility_of_element_located(locator))
        except Exception as e:
            print(f"find_ele, 查找元素失败: {e}")
            return False
        else:
            print("find_ele，找到了可见元素")
            return obj







    def find_child_eles(self, locator, child):
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            parent_elem = wait.until(lambda x: x.find_element(*locator))
            child_elements = parent_elem.find_elements(*child)
        except Exception as e:
            print(f"find_child_eles,查找元素失败{e}")
            return False
        else:
            return child_elements

    def input(self, locator, values):
        """ 输入框当中输入内容 """
        # print(locator,values)
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            obj = wait.until(lambda x: x.find_element(*locator))
            # print("input_ele",obj)
        except Exception as e:
            print(f"input,输入内容元素无法定位{e}")
            return False
        else:
            obj.send_keys(values)

    def redome_str(self, locator, redomestr):
        """
            locator:元素
            redomeTuple：(随机类型（0有特殊符号，1是数字+字母，2是纯字母），最小值，最大值)
        """
        # print(locator,values)
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            obj = wait.until(lambda x: x.find_element(*locator))
        except Exception as e:
            print(f"redome_str,密码元素无法定位{e}")
            return False
        else:
            try:
                redomeTuple = eval(redomestr)
            except:
                redomeTuple = ast.literal_eval(redomestr)

            pwd = redomeTuple[0]
            masL = redomeTuple[1]
            maxL = redomeTuple[2]

            values = self.usego.redome_string(pwd, masL, maxL)

            obj.send_keys(values)

    def clear(self, locator):
        """ 清空输入框中的内容 """
        el = self.driver.find_element(*locator)
        el.clear()

    def get_element_text(self, locator):
        """ 元素定位,获取text文本 """
        wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        try:
            obj = wait.until(lambda x: x.find_element(*locator))
        except Exception as e:
            print("查找文本类元素失败")

            return False
        else:
            return obj.text

    def is_text_exist(self, text: str, wait_seconds: int = 10) -> bool:
        """ 判断text是否于当前页面存在 """
        for i in range(wait_seconds):
            if text in self.driver.page_source:
                return True
            time.sleep(1)
        return False

    def is_loaded(self, url, timeout=8):
        """ 判断某个 url 是否被加载 """
        return WebDriverWait(self.driver, timeout).until(when.url_contains(url))

    def get_element_attribute(self, locator, expected):
        """ 获取某个元素的属性 """
        el = self.driver.find_element(*locator)
        return el.get_attribute(expected)

    def get_toast_text(self):
        """ toast弹窗/获取toast文本内容 """
        toast = self.driver.find_element("xpath", "//android.widget.Toast")
        return toast.text

    def set_attribute(self, locator, name, value):
        """ 设置元素属性（12306） """
        el = self.driver.find_element(*locator)
        jss = f'arguments[0].{name} = f"{value}"'
        self.driver.execute_script(jss, el)


######################################################################## scrollJS ####################################################################################


class scrollJS(basis):
    def scroll_to_bottom(self):
        """ 滚动到页面底部，使用js操作 """
        js = "window.scrollTo(0,document.body.scrollHeight)"
        self.driver.execute_script(js)

    def scroll_window(self, jss):
        return self.driver.execute_script(jss)  # 滑动到具体位置

    def scroll_ele_view(self, locator, jss):
        # wait = WebDriverWait(self.driver, timeout=20, poll_frequency=1)
        # obj = wait.until(lambda x: x.find_element(*locator))
        obj = self.driver.find_element(*locator)

        return self.driver.execute_script(jss, obj)  # 滑动到具体位置


######################################################################### other ####################################################################################




if __name__ == '__main__':
    pass