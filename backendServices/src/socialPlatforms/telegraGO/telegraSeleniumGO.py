# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/16 00:47
@Author ： eblis
@File ：telegraSelenium.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import re
import sys
import time
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
        # print(f"接收到的数据 {title},content:{content}")
        # 生成标题
        driver = None
        try:
            # 初始化浏览器驱动
            driver = self.ads.basicEncapsulation(adsUser, configCall.adsServer)

            try:
                driver.get("https://telegra.ph/")
            except Exception as e:
                print(f"driver.get 出现异常: {e}")
                return None

            # 等待页面元素加载
            wait = WebDriverWait(driver, 10)

            try:
                # 设置标题
                title_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/h1')))
                driver.execute_script("arguments[0].textContent = arguments[1];", title_input, title)
            except Exception as e:
                print(f"标题设置失败: {e}")
                return None

            try:
                # 设置内容输入框为空
                content_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_tl_editor"]/div[1]/p')))
                driver.execute_script("arguments[0].textContent = '';", content_input)
            except Exception as e:
                print(f"内容输入框设置失败: {e}")
                return None

            self.add_content_to_page(driver, content, content_input)


            # 发布文章
            try:
                publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_publish_button"]')))
                driver.execute_script("arguments[0].click();", publish_button)
            except Exception as e:
                print(f"点击发布按钮失败: {e}")
                return None

            # 随机等待一段时间
            time.sleep(self.usego.randomRandint(5, 10))
            return driver.current_url

        except Exception as e:
            print(f"页面操作失败: {e}")
            return None

        finally:
            if driver:
                self.ads.adsAPI(configCall.adsServer, "stop", adsUser)

    def add_content_to_page(self, driver, content, content_input):
        # 判断 content 是否包含 HTML 标签
        def has_html_tags(content):
            return bool(re.search(r'<.*?>', content))

        try:
            if has_html_tags(content):  # 如果 content 中包含 HTML 标签
                # 如果 content 中包含 HTML 标签，使用脚本创建元素
                script = self.convert_to_js_script(content)  # 使用之前的 convert_to_js_script 方法
                driver.execute_script(f"""
                    {script}
                """, content_input)
            else:  # 如果 content 不包含 HTML 标签，直接将文本插入
                driver.execute_script("""
                    var p = document.createElement('p');
                    p.textContent = arguments[0];
                    arguments[1].appendChild(p);
                """, content, content_input)
        except Exception as e:
            print(f"添加文章内容失败: {e}")
            return None

    def convert_to_js_script(self, content):
        """
        Converts an HTML string into a JavaScript string suitable for driver.execute_script.

        Args:
            content (str): The HTML content to be converted.

        Returns:
            str: The JavaScript script string.
        """

        def parse_html_to_js(content, parent="arguments[0]"):
            js_lines = []

            # Regular expression to match opening tag, attributes, and inner content
            tag_pattern = re.compile(r'<(\w+)([^>]*)>(.*?)<\/\1>', re.DOTALL)

            # Match individual tags and their content
            tags = tag_pattern.findall(content)

            for tag, attrs, inner_html in tags:
                if tag == 'img':
                    # Handle <img> tags
                    src_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', attrs)
                    if src_match:
                        img_src = src_match.group(1)
                        js_lines.append(f"var img = document.createElement('img');")
                        js_lines.append(f"img.src = '{img_src}';")
                        js_lines.append(f"{parent}.appendChild(img);")
                elif tag == 'a':
                    # Handle <a> tags with potential nested content
                    href_match = re.search(r'href=[\'"]([^\'"]+)[\'"]', attrs)
                    if href_match:
                        href = href_match.group(1)
                        js_lines.append(f"var a = document.createElement('a');")
                        js_lines.append(f"a.href = '{href}';")
                        # Process nested HTML inside <a> (e.g., <img>)
                        nested_js = parse_html_to_js(inner_html, parent="a")
                        js_lines.extend(nested_js if nested_js else [])
                        js_lines.append(f"{parent}.appendChild(a);")
                elif tag in ['p', 'h2', 'h3', 'h4']:
                    # Handle common tags like <p>, <h2>, etc.
                    js_lines.append(f"var {tag} = document.createElement('{tag}');")
                    nested_js = parse_html_to_js(inner_html, parent=tag)  # Process nested content
                    if nested_js:
                        js_lines.extend(nested_js)
                    else:
                        # Escape special characters for text content
                        js_lines.append(f"{tag}.textContent = `{escape(inner_html.strip())}`;")
                    js_lines.append(f"{parent}.appendChild({tag});")
                else:
                    # Generic fallback for other tags
                    js_lines.append(f"var {tag} = document.createElement('{tag}');")
                    nested_js = parse_html_to_js(inner_html, parent=tag)
                    if nested_js:
                        js_lines.extend(nested_js)
                    else:
                        js_lines.append(f"{tag}.textContent = `{escape(inner_html.strip())}`;")
                    js_lines.append(f"{parent}.appendChild({tag});")

            return js_lines

        # Start parsing and join lines
        js_lines = parse_html_to_js(content)
        return '\n'.join(js_lines)



if __name__ == '__main__':
    tele = telegraSeleniumGO()
    adsUser = "kpom9ou"
    title = "你还好吗？"
    content = """<h2>冬の旅の魅力</h2>
<p>冬の旅は、雪景色に包まれた神秘的な世界への冒険です。白銀の世界に身を委ね、静寂と清らかな空気に包まれると、心も体もリフレッシュされます。雪の結晶が舞い落ちる幻想的な風景は、まるで夢の中にいるような感覚を与えてくれます。寒さを忘れて、暖かい飲み物を楽しみながら、冬の旅の魅力に魅了されることでしょう。冬の旅に出かけ、新たな冒険を楽しんでみませんか。</p>

<h3>関連リンク</h3>
<p><a href='https://baidu.com' target='_blank'>https://baidu.com</a></p>
<p><a href='https://support.google.com/websearch/answer/181196?hl=zh-CN' target='_blank'>无障碍功能帮助</a></p>"""
    tele.run(adsUser, title, content)
