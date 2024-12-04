# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/12/2 21:16
@Author ： eblis
@File ：aiGO.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import time
import openai

from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.public.commonUse import otherUse, customCache
import middleware.public.configurationCall as configCall

class aiGO():
    def __init__(self):
        self.artsql = article_sqlGO()
        self.usego = otherUse()
        self.cache = customCache()

    def run(self, trainingPhrases, max_retries=5, timeout=60, wait_time=10):

        AIbase = self.witchOPEN()
        if AIbase is not None:
            if AIbase["url"] != "":
                try:
                    self.usego.sendlog("使用新的openai")
                    openai.api_base = f'{AIbase["url"]}'
                except Exception as e:
                    self.usego.sendlog(f"openai.api_base失败：{e}")
            else:
                self.usego.sendlog("使用旧的 ")

            retries = 0
            # 设置OpenAI API密钥
            openai.api_key = AIbase["key"]

            while retries < max_retries:
                try:
                    self.usego.sendlog(f'正在使用{AIbase["model"]} 对 {trainingPhrases} 进行训练！！')
                    response = openai.ChatCompletion.create(
                        model=f'{AIbase["model"]}',
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
                    self.usego.sendlog(f" 生成的结果：{generated_text}")
                    # article = self.insert_article(generated_text)
                    return generated_text

                except openai.error.RateLimitError:
                    self.usego.sendlog(f"达到速率限制，等待 {wait_time} 秒后重试")
                    time.sleep(wait_time)
                    retries += 1
            # raise Exception("重试次数达到上限，请求失败")
            return None
        else:
            return None

    def witchOPEN(self):
        """
            @Datetime ： 2024/12/3 21:27
            @Author ：eblis
            @Motto：简单描述用途
        """
        cache_key = configCall.aiKey
        cached_data = self.cache.read_from_cache(cache_key)

        if cached_data:
            self.usego.sendlog(f"从缓存中获取数据{cached_data}")
            return cached_data

        sql_data = self.artsql.ai_open_api_sql(f"{cache_key}")

        if "sql 语句异常" not in str(sql_data):
            resdatas = [item[0] for item in sql_data]
            self.usego.sendlog(f"数据库查询结果{resdatas}" )
            if resdatas != []:
                AIbase = self.usego.changeDict(resdatas[0])
                self.cache.write_to_cache(cache_key, AIbase)
                return AIbase
            else:
                self.usego.sendlog("数据库没有想要的数据")
                return None
        else:
            self.usego.sendlog("访问数据库失败了，请重试")
            return None
