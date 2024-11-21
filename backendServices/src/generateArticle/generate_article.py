# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/18 22:16
@Author ： eblis
@File ：generate_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import os
import sys
import time
from datetime import datetime
import re
import openai

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.awsMQ.amazonSQS import AmazonSQS

class generateArticle():
    def __init__(self):
        self.ssql = article_sqlGO()
        self.basql = basis_sqlGO()
        self.usego = otherUse()
        self.aws_sqs = AmazonSQS()

    def run(self, pcname, queue_url, max_length, isopenAI, type, promptID, sortID,  theme, Keywords, ATag, link, language, user):
        """
            @Datetime ： 2024/11/18 22:19
            @Author ：eblis
            @Motto：简单描述用途
        """

        # 第一步:根据promptID 拿到具体prompt信息

        promptDD = self.witch_prompt(promptID)
        if promptDD is not None and len(promptDD) > 0:
            # # 第二步 根据 prompt 的初始化
            promptList = self.disassembly(promptDD, max_length, theme, Keywords, ATag, link, language, user)

            self.lesGO(isopenAI, type, promptID, sortID, promptList, user)
            time.sleep(5)
            sql_data = self.basql.pcSettings_update_state_sql(pcname, state=0)
            self.aws_sqs.deleteMSG(queue_url)

        else:
            return False
        
        
    def lesGO(self, isopenAI, type, promptID, sortID, promptList, user):
        """
            @Datetime ： 2024/11/19 17:19
            @Author ：eblis
            @Motto：简单描述用途
        """
        sql_data = self.ssql.ai_open_api_sql("OPEN_API_KEY")
        if "sql 语句异常" not in str(sql_data):
            resdatas = [item[0] for item in sql_data]
            api_key = resdatas[0]
        else:
            print("访问数据库失败了，请重试")
            return False

        for i in range(len(promptList)):
            thisArticle = promptList[i]
            print(f"开始{i} prompt 组 生成文章")
            print(f"这篇文章由{len(thisArticle)} 段组成")
            Epilogue = ''
            article_title = ''

            for j in range(len(thisArticle)):
                if thisArticle[j]["type"] == "0" or thisArticle[j]["type"] == 0:
                    if int(isopenAI) == 0:
                        print(f"openAI 很高兴 为你服务")

                        print(f"哟！好样的，需要生成{len(promptList)} 这么多篇文章啊！")

                        generated_text = self.generate_article(thisArticle[j]["promptdata"], api_key)
                        if article_title == "":
                            title_prompt = f"需求：1、根据{generated_text} 所使用的语言，给出一端30字符以内的总结； 2、总结末尾不带任何标点符号；"
                            title_text = self.generate_article(title_prompt, api_key)
                            article_title = title_text
                        else:
                            print(f"当前标题：{article_title} ")

                        Epilogue += f"\n\n {generated_text}\n\n"
                    else:
                        print(f"来了老弟")
                        print("还没对接")
                        return False
                else:

                    Epilogue += f'\n\n {thisArticle[j]["promptdata"] }\n\n'

            print(f"第{i} 篇文章生成完比，剩余{len(promptList) - 1}:{Epilogue}")
            self.conversionType(api_key, article_title, Epilogue, type, promptID, sortID,  user)

        return True

    def convert_to_markdown(self, text):
        # 替换裸链接为 Markdown 格式
        text = re.sub(r'(?<!\()https?://[^\s<>]+', lambda m: f"[链接]({m.group(0)})", text)

        # 替换 HTML 链接为 Markdown 格式
        text = re.sub(r"<a href=['\"](https?://[^\s<>]+)['\"]>(.*?)</a>", r"[\2](\1)", text)

        # 按逻辑段落分段
        paragraphs = text.split("\n\n")
        markdown_output = "\n\n".join(paragraph.strip() for paragraph in paragraphs)

        return markdown_output
    
    def conversionType(self, api_key, article_title, Epilogue, type, promptID, sortID,  user):
        """
            @Datetime ： 2024/11/20 14:55
            @Author ：eblis
            @Motto：简单描述用途
        """
        print(f"根据 {type}  优化内容")
        htmllist = ["HTML", "Html", "html"]
        downlist = ["Markdown", "markdown", "MARKDOWN"]
        if type in htmllist:
            new_prompt = f"请将 {Epilogue} 转换为完整的 HTML 代码，包括段落排版、超链接处理（在新标签页打开），并使用适当给段落赋予<h2>、<h3>、<h4> 标题 的 HTML 标签结构。"
            title_text = self.generate_article(new_prompt, api_key)
        elif type in downlist:
            new_Epilogue = self.convert_to_markdown(Epilogue)
            new_prompt = f"请将 {new_Epilogue} 转换为完整的 Markdown 代码，包括段落排版、超链接处理（在新标签页打开），并使用适当段落赋予2级、3级、4级 标题 Markdown 标签结构。"
            title_text = self.generate_article(new_prompt, api_key)

        else:
            title_text = Epilogue

        sql_data = self.save_sql(isopenAI, promptID, sortID, article_title, title_text, type, user)
        if "sql 语句异常" not in str(sql_data):
            print("入库成功")
        else:
            print("入库失败")
    


    def save_sql(self, isopenAI, promptID, sortID, title, content, type, user):
        """
            @Datetime ： 2024/11/19 22:14
            @Author ：eblis
            @Motto：简单描述用途
        """

        create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if int(isopenAI) == 0:
            source = "openAI"
        else:
            source = "OllamaAI"

        if user == []:
            print(f"生成通用文章")
            user = ""
            commission = 1
        else:
            print(f"要生成专属文章哦")
            user = user[0]
            commission = 0
        self.ssql.article_insert_sql(promptID, sortID, source, title, content, type, user, commission, create_at)


    def generate_article(self, trainingPhrases, api_key, max_retries=5, timeout=60, wait_time=10):
        retries = 0
        # print("api_key", api_key)
        openai.api_key = api_key

        while retries < max_retries:
            try:
                print(f'正在使用{trainingPhrases} 进行训练！！')
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user",
                         "content": trainingPhrases
                         }
                    ],
                    max_tokens=2000,
                    n=1,
                    temperature=0.7,
                    timeout=timeout,
                )
                generated_text = response['choices'][0]['message']['content'].strip()
                print(f" 生成的结果：{generated_text}")
                # article = self.insert_article(generated_text)

                return generated_text

            except openai.error.RateLimitError:
                print(f"达到速率限制，等待 {wait_time} 秒后重试")
                time.sleep(wait_time)
                retries += 1
        raise Exception("重试次数达到上限，请求失败")


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
                    new_prompt["promptdata"] = this_prompt
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
        sql_data = self.ssql.ai_prompt_select_sql(promptID)
        if "sql 语句异常" not in str(sql_data):
            resdatas = [item[4] for item in sql_data]
            try:
                resdatas_list = json.loads(resdatas[0])
                return resdatas_list
            except json.JSONDecodeError as e:
                print(f"转换异常：{e}")
                return None
        else:
            return None


if __name__ == '__main__':
    Art = generateArticle()
    pcname = "this_mac_1_not"
    queue_url = "/"
    max_length = 2
    isopenAI = 0
    promptID = 1
    sortID = 1
    theme = ["爱情", "爱情"]
    Keywords = ["浪漫", "忧伤"]
    ATag = ['<a jsname="KI37ad" class="gyPpGe" href="https://support.google.com/websearch/answer/181196?hl=zh-CN" ping="/url?sa=t&amp;source=web&amp;rct=j&amp;url=https://support.google.com/websearch/answer/181196%3Fhl%3Dzh-CN&amp;ved=0ahUKEwjYhv3unOuJAxWzevUHHbs_CKgQwcMDCAY&amp;opi=89978449">无障碍功能帮助</a>','<a jsname="KI37ad" class="gyPpGe" href="https://support.google.com/websearch/answer/181196?hl=zh-CN" ping="/url?sa=t&amp;source=web&amp;rct=j&amp;url=https://support.google.com/websearch/answer/181196%3Fhl%3Dzh-CN&amp;ved=0ahUKEwjYhv3unOuJAxWzevUHHbs_CKgQwcMDCAY&amp;opi=89978449">无障碍功能帮助</a>']
    link = ["https://www.example.com", "https://www.baidu.com"]
    language = ["中文", "英语"]
    user = []
    type = "Markdown"

    Art.run(pcname, queue_url, max_length, isopenAI, type, promptID, sortID, theme, Keywords, ATag, link, language, user)



