# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/25 20:45
@Author ： eblis
@File ：post_sql_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from middleware.dataBaseGO.article_sqlCollenction import article_sqlGO
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.awsMQ.amazonSQS import AmazonSQS

class postSqlArticle():
    def __init__(self):
        self.ssql = article_sqlGO()
        self.basql = basis_sqlGO()
        self.usego = otherUse()
        self.aws_sqs = AmazonSQS()

    def run(self, pcname, queue_url, platform, group, post_max, sortID, type,  source, commission, isAI, user):
        """
            @Datetime ： 2024/11/18 22:19
            @Author ：eblis
            @Motto：简单描述用途
        """

        # 第一步：先将符合要求的数据读取

    def withcPlatform(self, platform, group, post_max,):
        """
            @Datetime ： 2024/11/25 20:52
            @Author ：eblis
            @Motto：简单描述用途
        """
        if platform == "blogger":
            sql_data = self.basql.ai_prompt_select_sql(promptID)
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



