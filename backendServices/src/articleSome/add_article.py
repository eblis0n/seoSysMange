# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/18 22:16
@Author ： eblis
@File ：add_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import os
import sys
from datetime import datetime
import re

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse
import middleware.public.configurationCall as configCall
from backendServices.src.articleSome.public.aiGO import aiGO
from backendServices.src.awsMQ.amazonSQS import AmazonSQS

from bs4 import BeautifulSoup

class generateArticle():
    def __init__(self):
        self.artsql = article_sqlGO()
        self.basql = basis_sqlGO()
        self.usego = otherUse()
        self.aws_sqs = AmazonSQS()
        self.aigo = aiGO()

    def run(self, pcname, queue_url, max_length, source, type, promptID, sortID,  theme, Keywords, ATag, link, language, user, receipt_handle):
        """
            @Datetime ： 2024/11/18 22:19
            @Author ：eblis
            @Motto：简单描述用途
        """

        # 第一步:根据promptID 拿到具体prompt信息
        print(f"来活啦～{pcname}, {queue_url}, {max_length}, {source}, {type}, {promptID}, {sortID},  {theme}, {Keywords}, {ATag}, {link}, {language}, {user}")

        promptDD = self.witch_prompt(promptID)
        if promptDD is not None and len(promptDD) > 0:
            print("第二步 根据 prompt 的初始化")
            promptList = self.disassembly(promptDD, max_length, theme, Keywords, ATag, link, language, user)
            print("第3步 很关键，生成文章")
            outcome = self.lesGO(source, type, promptID, sortID, promptList,  user)

            sql_data = self.basql.pcSettings_update_state_sql(pcname, state=0)
            self.aws_sqs.deleteMSG(queue_url, receipt_handle)
            # print("恭喜你，生成文章任务完成")
            return outcome

        else:
            return False
        
        
    def lesGO(self, source, type, promptID, sortID, promptList, user):
        """
            @Datetime ： 2024/11/19 17:19
            @Author ：eblis
            @Motto：简单描述用途
        """
        for i in range(len(promptList)):
            thisArticle = promptList[i]
            print(f"开始{i} prompt 组 生成文章")
            print(f"这篇文章由{len(thisArticle)} 段组成")
            Epilogue = ''
            article_title = ''
            language = ''

            for j in range(len(thisArticle)):
                print(f"这组Article：{thisArticle[j]}")
                link = thisArticle[j]['link']
                try:
                    language = thisArticle[j]["language"]
                except:
                    print(f'thisArticle[j]["language"]： 为{thisArticle[j]["language"]} 跳过')

                if int(thisArticle[j]["type"]) == 0:
                    if source == "openAI":
                        print(f"openAI 很高兴 为你服务")

                        print(f"哟！好样的，需要生成{len(promptList)} 这么多篇文章啊！")

                        generated_text = self.aigo.run(thisArticle[j]["promptdata"])
                        if generated_text is not None:
                            if article_title == "":
                                title_prompt = f"Requirements: 1. Based on the language used by {generated_text}, give a summary within 30 characters at one end; 2. Without any punctuation marks;"
                                title_text = self.aigo.run(title_prompt)
                                article_title = title_text
                            else:
                                print(f"当前标题：{article_title} ")
                            new_generated_text = self.replace_url_with_regex(generated_text, link)

                            Epilogue += f"\n{new_generated_text}\n"
                        else:
                            print("AI跪了。需要重试")
                            continue
                    elif source == "OllamaAI":
                        print(f"OllamaAI 还没对接，敬请期待")

                        return False
                    else:
                        print(f"来了老弟")
                        print("还没对接")
                        return False
                else:
                    Epilogue += f'\n {thisArticle[j]["promptdata"] }\n'

            self.conversionType(source, article_title, Epilogue, language, type, promptID, sortID,  user)
            print(f"第{i} 篇文章生成完比，剩余{len(promptList) - 1}")
        return True

    def replace_url_with_regex(self, text, replacement_url):
        """
        使用正则表达式替换文本中包含特定域名的 URL。

        :param text: 原始文本
        :param replacement_url: 替换后的 URL
        :return: 替换后的文本
        """
        pattern = r"https://www\.example\.com(\S*)"
        return re.sub(pattern, replacement_url, text)

    def convert_to_markdown(self, text):
        # 替换裸链接为 Markdown 格式
        text = re.sub(r'(?<!\()https?://[^\s<>]+', lambda m: f"[链接]({m.group(0)})", text)

        # 替换 HTML 链接为 Markdown 格式
        text = re.sub(r"<a href=['\"](https?://[^\s<>]+)['\"]>(.*?)</a>", r"[\2](\1)", text)

        # 按逻辑段落分段
        paragraphs = text.split("\n\n")
        markdown_output = "\n\n".join(paragraph.strip() for paragraph in paragraphs)

        return markdown_output
    
    def conversionType(self, source, article_title, Epilogue, language, type, promptID, sortID, user):
        """
            @Datetime ： 2024/11/20 14:55
            @Author ：eblis
            @Motto：将生成的内容 修改为指定模式
        """
        print(f"根据 {type}  优化{Epilogue} 内容")
        htmllist = ["HTML", "Html", "html"]
        downlist = ["Markdown", "markdown", "MARKDOWN"]
        if type in htmllist:
            new_prompt = f"""{configCall.addConvertHtml}"""
            content = self.aigo.run(new_prompt)
            if content is not None:
                check_html = self.extract_body_content(content)
                try:
                    soup = BeautifulSoup(check_html, "html.parser")
                    detail = soup.body.decode_contents()
                except:
                    detail = check_html
            else:
                detail = Epilogue
        elif type in downlist:
            # new_Epilogue = self.convert_to_markdown(Epilogue)
            new_prompt = f"""{configCall.addConvertMarkdowm}"""
            detail = self.aigo.run(new_prompt)
            if detail is None:
                detail = Epilogue
        else:
            print(f"不认识这个{type},保留原文格式")
            detail = Epilogue

        self.save_sql(source, promptID, sortID, article_title, detail, language, type, user)

    def extract_body_content(self, html_content):
        """
        @Datetime ： 2024/12/4 20:23
        @Author ：eblis
        @Motto：提取 HTML 中 <body> 标签内的内容。
        """
        # 使用正则表达式提取 <body> 标签中的内容
        match = re.search(r"<body.*?>(.*?)</body>", html_content, flags=re.IGNORECASE | re.DOTALL)

        if match:
            # 提取 <body> 标签内的内容
            body_content = match.group(1)
            return body_content.strip()
        else:
            # 如果没有 <body> 标签，返回空字符串
            return html_content

    def save_sql(self, source, promptID, sortID, title, content, language, type, user):
        """
            @Datetime ： 2024/11/19 22:14
            @Author ：eblis
            @Motto：简单描述用途
        """

        # print(f"接收到的参数：{source}, {promptID}, {sortID}, {title}, {content}, {language}, {type}, {user}")
        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if user == []:
            print(f"生成通用文章")
            user = ""
            commission = 1
        else:
            print(f"要生成专属文章哦")
            user = user[0]
            commission = 0
        sql_data = self.artsql.ai_article_insert_sql(0, promptID, sortID, source, title, content, language, type, user, commission, create_at)
        if "sql 语句异常" not in str(sql_data):
            print("入库成功")
            return True
        else:
            print("入库失败")
            return False


    def disassembly(self, promptDD, max_length, theme, Keywords, ATag, link, language, user):
        """
            @Datetime ： 2024/11/19 15:07
            @Author ：eblis
            @Motto：简单描述用途
        """
        prompt_list = []
        for i in range(int(max_length)):
            single_prompt_list = []
            # 获取对应索引的值，若不存在则设为空字符串
            try:
                current_theme = theme[i] if i < len(theme) else ""
            except:
                current_theme = ""

            try:
                current_Keywords = Keywords[i] if i < len(Keywords) else ""
            except:
                current_Keywords = ""

            try:
                # 检查 Atab 是否有该索引，如果没有，赋值为空字符串
                current_ATag = ATag[i] if i < len(ATag) else ""
            except:
                current_ATag = ""

            try:
                current_link = link[i] if i < len(link) else ""
            except:
                current_link = ""


            try:
                current_language = language[i] if i < len(language) else ""
            except:
                current_language = ""

            try:
                current_user = user[i] if i < len(user) else ""
            except:
                current_user = ""

            for data in promptDD:
                new_prompt = {}
                if data["type"] == 0 or data["type"] == "0":
                    prompt_template = data["promptdata"]  # 获取当前的 prompt 模板

                    this_prompt = (
                        prompt_template
                        .replace('{theme}', current_theme)
                        .replace('{Keywords}', current_Keywords)
                        .replace('{ATag}', current_ATag)
                        .replace('{link}', current_link)
                        .replace('{language}', current_language)
                        .replace('{user}', current_user)
                    )
                    new_prompt["type"] = data["type"]
                    new_prompt["link"] = current_link
                    new_prompt["ATag"] = current_ATag
                    new_prompt["promptdata"] = this_prompt
                    new_prompt["language"] = current_language
                else:
                    # this_prompt = data["promptdata"]
                    new_prompt = data
                single_prompt_list.append(new_prompt)
            # 将每组生成的结果添加到最终结果列表
            prompt_list.append(single_prompt_list)
        return prompt_list
            
            
    def witch_prompt(self, promptID):
        """
            @Datetime ： 2024/11/18 22:42
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"提取promptID 得到具体prompt")
        sql_data = self.artsql.ai_prompt_select_sql(promptID)
        if "sql 语句异常" not in str(sql_data):
            resdatas = [item[5] for item in sql_data]

            print(f"提取到的resdatas:{resdatas}")
            if resdatas!=[]:
                try:
                    resdatas_list = json.loads(resdatas[0])
                    return resdatas_list
                except json.JSONDecodeError as e:
                    print(f"转换异常：{e}")
                    return None
            else:
                print("获取数据失败了")
                return None

        else:
            return None


if __name__ == '__main__':
    Art = generateArticle()
    pcname = "this_mac_1_not"
    queue_url = "/"
    max_length = 1
    source = "openAI"
    promptID = 4
    sortID = 5
    theme = ['大化け期待！2024年の東証スタンダードで注目のテンバガー候補銘柄']
    Keywords = []
    ATag = []
    link = ["https://note.com/easy_racoon9308/n/n0228a186ba82"]
    language = ["jp"]
    user = []
    type = "Markdown"


    Art.run(pcname, queue_url, max_length, source, type, promptID, sortID, theme, Keywords, ATag, link, language, user)



