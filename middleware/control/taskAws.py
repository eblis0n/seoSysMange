# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/14 17:04
@Author ： eblis
@File ：taskAws.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse

from backendServices.src.awsMQ.amazonSQS import AmazonSQS


class taskAws():
    def __init__(self):

        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()

        self.usego = otherUse()
        self.aws_sqs = AmazonSQS()

    def run(self, type, platform, datasDict):
        """
            @Datetime ： 2024/11/14 17:06
            @Author ：eblis
            @Motto：简单描述用途
        """
        results = []
        self.usego.sendlog(f"{type} ,{platform}进来了")
        clientL = self.witchClient(platform)
        self.usego.sendlog(f"有{len(clientL)} 设备 符合 条件，准备执行 {type}")
        if clientL != []:
            if type == "splice":
                self.isSplice(results, clientL, datasDict)
                return results
            elif type == "cookies":
                self.iscookie(results, clientL, datasDict)
                return results
            elif type == "article":
                self.isarticle(results, clientL, datasDict)
                return results
            elif type == "postSqlArticle":
                self.isPostSqlArticle(results, clientL, datasDict)
                return results
            else:
                self.usego.sendlog("啥也不是！！")
                return False



    def witchClient(self, platform):
        """
            @Datetime ： 2024/11/14 17:10
            @Author ：eblis
            @Motto：简单描述用途
        """

        self.usego.sendlog(f"第一步，先查数据库，查看{platform}是否存在符合条件的PC")
        # state=3 是 实际查询为 state !=2
        sql_data = self.ssql.pcSettings_select_sql(state=3)
        clientList = []
        if "sql 语句异常" in str(sql_data):
            return []
        else:
            resdatas = [{'id': item[0],
                         'group': item[1],
                         'name': item[2],
                         'address': item[3],
                         'account': item[4],
                         'password': item[5],
                         'platform': item[6],
                         'state': item[7],
                         'remark': item[8],
                         'create_at': self.usego.turn_isoformat(item[9]),
                         'update_at': self.usego.turn_isoformat(item[10])
                         } for item in sql_data]
            self.usego.sendlog(f"第2步，根据 {type(platform)},{platform} 返回 符合条件的设备")

            for i in range(len(resdatas)):
                self.usego.sendlog(f'第{i} 台设备{resdatas[i]}')
                if platform in resdatas[i]["platform"]:
                    clientList.append(resdatas[i])


        return clientList

    def find_limit(self, idx):
        """
            @Datetime ： 2024/11/10 21:00
            @Author ：eblis
            @Motto：简单描述用途
        """
        end = 200000
        if idx == 0:
            start = 0
            # end = 200000
        else:
            start = end
            end = 200000 * (idx + 1)

        return start, end

    def iscookie(self, results, clientL, datasDict):
        """
            @Datetime ： 2024/11/14 19:58
            @Author ：eblis
            @Motto：简单描述用途
        """

        for idx, client in enumerate(clientL):
            result = {}
            # 生成 队列
            response = self.aws_sqs.initialization(f'client_{client["name"]}')
            self.usego.sendlog(f'Amazon SQS队列 请求结果：{response}')

            queue_url = response['QueueUrl']
            self.usego.sendlog(f'{idx}, name:client_{client["name"]}，state:{client["state"]}，队列地址:{queue_url}')
            task_data = {
                'pcname': client["name"],
                'queue_url': queue_url,
                'adsIDlist': datasDict["adsIDlist"],
            }
            self.usego.sendlog(f' getCookie，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f'run_getCookie_group',
                                            f'getCookie',
                                            task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_{datasDict["platform"]}_selenium，任务发送结果:{response}')

            # 将 执行pc 状态 修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")
            break

    
    def isSplice(self, results, clientL, datasDict):
        """
            @Datetime ： 2024/11/14 17:16
            @Author ：eblis
            @Motto：发拼接， 搭配find_limit一起使用
        """

        self.usego.sendlog(f'发拼接')
        query = {
            "genre": str(datasDict["genre"]),
            "platform": str(datasDict["platform"]),
            "sort": str(datasDict["sort"]),
        }
        total = self.mossql.splicing_interim_find_count("seo_external_links_post", query)
        self.usego.sendlog(f'第二步，本次任务一共需要执行{total} 连接')
        if total == 0:
            return False

        sum = 0
        idx = 0  # 初始化索引
        while idx < len(clientL) and sum < total:  # 条件控制循环
            client = clientL[idx]  # 获取当前索引对应的客户端数据
            self.usego.sendlog(f"{client} get ready")
            result = {}
            # 生成队列
            response = self.aws_sqs.initialization(f'client_{client["name"]}')
            queue_url = response['QueueUrl']
            self.usego.sendlog(f'{idx}, name:client_{client["name"]}，state:{client["state"]}，队列地址:{queue_url}')
            start, end = self.find_limit(idx)
            task_data = {
                'pcname': client["name"],
                'queue_url': queue_url,
                'genre': datasDict["genre"],
                'platform': datasDict["platform"],
                'stacking_min': datasDict["stacking_min"],
                'stacking_max': datasDict["stacking_max"],
                'title_alt': datasDict["title_alt"],
                'alt_text': datasDict["alt_text"],
                'sort': datasDict["sort"],
                'isarts': datasDict["isarts"],
                'postingStyle': datasDict["postingStyle"],
                'group': datasDict["group"],
                'start': start,
                'end': end
            }
            self.usego.sendlog(f' run_post_spliceGo，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f'run_post_spliceGo_group', f'run_post_spliceGo', task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_post_spliceGo，执行的是{task_data["platform"]},任务发送结果:{response}')

            # 将执行PC状态修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")

            # 手动增加索引
            idx += 1
            sum += 200000

        self.usego.sendlog(f"任务分派完成：一共使用:{idx}, 完成{sum} 数据 执行")


    def isarticle(self, results, clientL, datasDict):
        """
            @Datetime ： 2024/11/14 19:58
            @Author ：eblis
            @Motto：生成文章
        """

        for idx, client in enumerate(clientL):
            result = {}
            # 生成 队列
            response = self.aws_sqs.initialization(f'client_{client["name"]}')
            queue_url = response['QueueUrl']
            self.usego.sendlog(f'{idx}, name:client_{client["name"]}，state:{client["state"]}，队列地址:{queue_url}')

            task_data = {
                'pcname': client["name"],
                'queue_url': queue_url,
                'max_length': datasDict["max_length"],
                "source": datasDict["source"],
                "type": datasDict["type"],
                "promptID":  datasDict["promptID"],
                "sortID":  datasDict["sortID"],
                "theme": datasDict["theme"],
                "Keywords": datasDict["Keywords"],
                "ATag": datasDict["ATag"],
                "link": datasDict["link"],
                "language": datasDict["language"],
                "user": datasDict["user"],

            }
            self.usego.sendlog(f' get article，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f'run_generate_article_group',f'generate_article',task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_{datasDict["platform"]}_selenium，任务发送结果:{response}')

            # 将 执行pc 状态 修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")
            break
            
            
    def isPostSqlArticle(self, results, clientL, datasDict):
        """
            @Datetime ： 2024/11/25 19:47
            @Author ：eblis
            @Motto：从数据库获取文章 发布
        """
        for idx, client in enumerate(clientL):
            result = {}
            # 生成 队列
            response = self.aws_sqs.initialization(f'client_{client["name"]}')
            queue_url = response['QueueUrl']
            self.usego.sendlog(f'{idx}, name:client_{client["name"]}，state:{client["state"]}，队列地址:{queue_url}')

            task_data = {
                "platform": datasDict['platform'],
                "group": datasDict['group'],
                "post_max": datasDict['post_max'],
                "sortID": datasDict['sortID'],
                "type": datasDict['type'],
                "commission": datasDict['commission'],
                "isAI": datasDict['isAI'],
                "user": datasDict['user'],
                "language": datasDict['language'],
                "isSecondary": datasDict['isSecondary']
            }

            self.usego.sendlog(f'PostSqlArticle，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f'run_generate_article_group',
                                            f'postSqlArticle',
                                            task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_{datasDict["platform"]}_selenium，任务发送结果:{response}')

            # 将 执行pc 状态 修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")
            break
    



    


