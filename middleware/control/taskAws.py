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
        if type == "splice":
            resdatas = self.witchClient(platform)
            if resdatas != []:
                self.isSplice(results, resdatas, datasDict)
                return results
            else:
                self.usego.sendlog(f'有 {len(resdatas)} 设备符合')
                return False
        elif type == "cookies":
            resdatas = self.witchClient(platform)
            if resdatas != []:
                self.iscookie(results, resdatas, datasDict)
                return results
        elif type == "article":
            resdatas = self.witchClient(platform)
            if resdatas != []:
                self.isarticle(results, resdatas, datasDict)
                return results
        elif type == "postSqlArticle":
            resdatas = self.witchClient(platform)
            if resdatas != []:
                self.isPostSqlArticle(results, resdatas, datasDict)
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

        self.usego.sendlog("第一步，先查数据库，查看是否存在符合条件的PC")
        # state=3 是 实际查询为 state !=2
        sql_data = self.ssql.pcSettings_select_sql(platform= platform, state=3)

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
        return resdatas



    def iscookie(self, results, resdatas, datasDict):
        """
            @Datetime ： 2024/11/14 19:58
            @Author ：eblis
            @Motto：简单描述用途
        """

        for idx, client in enumerate(resdatas):
            result = {}
            # 生成 队列
            response = self.aws_sqs.initialization(f'client_{client["name"]}')
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

    
    def isSplice(self, results, resdatas, datasDict):
        """
            @Datetime ： 2024/11/14 17:16
            @Author ：eblis
            @Motto：发拼接， 搭配find_limit一起使用
        """

        query = {
            "genre": str(datasDict["genre"]),
            "platform": str(datasDict["platform"]),
            "sort": str(datasDict["sort"]),
        }
        total = self.mossql.splicing_interim_find_count("seo_external_links_post", query)
        self.usego.sendlog(f'第二步，本次任务一共需要执行{total} 连接')
        if total == 0:

            return False

        if len(resdatas) > 1 and total > 200000:
            self.usego.sendlog(f' 数据量很大，不能浪费设备')
            for idx, client in enumerate(resdatas):
                result = {}
                # 生成 队列
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

                # 将 执行pc 状态 修改
                sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
                self.usego.sendlog(f"pc执行结果{sql_data}")


        else:
            # 不满足条件，执行一次任务而不是循环
            self.usego.sendlog(f'小case ，一台设备就够玩了')
            client = resdatas[0]  # 只处理一个客户端
            result = {}
            response = self.aws_sqs.initialization(f'client_{client["name"]}')
            queue_url = response['QueueUrl']
            self.usego.sendlog(f'只处理一次，name:client_{client["name"]}，state:{client["state"]}，队列地址:{queue_url}')
            start, end = self.find_limit(0)  # 这里只处理第一个客户端，索引为0
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


            self.usego.sendlog(f' run_{datasDict["platform"]}_selenium，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f'run_{datasDict["platform"]}_group',
                                            f'run_{datasDict["platform"]}_selenium',
                                            task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_{datasDict["platform"]}_selenium，任务发送结果:{response}')

            # 将 执行pc 状态 修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")




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




    def isarticle(self, results, resdatas, datasDict):
        """
            @Datetime ： 2024/11/14 19:58
            @Author ：eblis
            @Motto：简单描述用途
        """

        for idx, client in enumerate(resdatas):
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
                "user": datasDict["user"],
                "theme": datasDict["theme"],
                "Keywords": datasDict["Keywords"],
                "ATag": datasDict["ATag"],
                "link": datasDict["link"],
                "language": datasDict["language"],

            }
            self.usego.sendlog(f' get article，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f'run_generate_article_group',
                                            f'generate_article',
                                            task_data)
            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_{datasDict["platform"]}_selenium，任务发送结果:{response}')

            # 将 执行pc 状态 修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")
            break
            
            
    def isPostSqlArticle(self, results, resdatas, datasDict):
        """
            @Datetime ： 2024/11/25 19:47
            @Author ：eblis
            @Motto：简单描述用途
        """
        for idx, client in enumerate(resdatas):
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
                "source": datasDict['source'],
                "commission": datasDict['commission'],
                "isAI": datasDict['isAI'],
                "user": datasDict['user']
            }

            self.usego.sendlog(f' PostSqlArticle，任务信息:{task_data}')
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
    



    


