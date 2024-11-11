# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 16:31
@Author ： eblis
@File ：outcome_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
from middleware.public.returnMsg import ResMsg

from flask import Blueprint, request
from src.api.urlSet import MyEnum
from middleware.dataBaseGO.basis_sqlCollenction import basis_sqlGO
from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse
from backendServices.src.socialPlatforms.telegraGO.telegraSelenium import telegraSelenium
from backendServices.src.assistance.spliceGo import spliceGo
from backendServices.src.awsMQ.amazonSQS import AmazonSQS


class splicingManage():
    def __init__(self):
        self.bp = Blueprint("splicing", __name__, url_prefix="/splicing")
        self.mossql = mongo_sqlGO()
        self.ssql = basis_sqlGO()
        self.Myenum = MyEnum()
        self.usego = otherUse()
        self.tele = telegraSelenium()
        self.aws_sqs = AmazonSQS()


        self.bp.route(self.Myenum.SPLICING_SUBMIT_PUSH, methods=['POST'])(self.splicing_submit_push)
        self.bp.route(self.Myenum.SPLICING_INSERT, methods=['POST'])(self.splicing_insert)
        self.bp.route(self.Myenum.SPLICING_LIST, methods=['GET'])(self.splicing_list)
        self.bp.route(self.Myenum.SPLICING_TOTAL, methods=['GET'])(self.splicing_total)
        self.bp.route(self.Myenum.SPLICING_DELETE_ALL, methods=['GET'])(self.splicing_delete_all)


    def splicing_list(self):
        """
            @Datetime ： 2024/10/21 00:28
            @Author ：eblis
            @Motto：简单描述用途
        """
        try:
            sql_data = self.mossql.splicing_interim_findAll("seo_external_links_post", end=10000)
        except Exception as e:
            self.usego.sendlog(f'list查询失败：{e}')
            sql_data = None

        resdatas = []

        if sql_data is not None:
            if len(sql_data) > 0:
                for i in range(len(sql_data)):
                    thisdata = {
                        "id": i,
                        "url": sql_data[i]["url"],
                        "platform": sql_data[i]["platform"],
                        "genre": sql_data[i]["genre"],
                        "sort": sql_data[i]["sort"],
                        "created_at": self.usego.turn_isoformat(sql_data[i]["created_at"])
                    }
                    resdatas.append(thisdata)

                self.usego.sendlog(f'list结果：{len(resdatas)}')
                res = ResMsg(data=resdatas)

            else:
                self.usego.sendlog(f'list结果：{len(resdatas)}')
                res = ResMsg(data=resdatas)

        else:
            self.usego.sendlog(f'list查询失败：{sql_data}')
            res = ResMsg(code='B0001', msg=f'list查询失败')


        return res.to_json()

    def splicing_insert(self):

        data_request = request.json

        url = data_request['url']
        genre = data_request['genre']
        platform = data_request['platform']
        sort = data_request['sort']

        url_list = url.split("\n")
        spl = spliceGo()

        try:
            zyurl = data_request['zyurl']

        except:
            self.usego.sendlog(f'自成一派')
            result = spl.splice_301(sort, genre, platform, url_list)
        else:
            if zyurl == "":
                result = spl.splice_301(sort, genre, platform, url_list)
            else:
                zyurl_list = zyurl.split("\n")
                result = spl.splice_301(sort, genre, platform, url_list, zyurl_list)

        if result is not None:
            self.usego.sendlog(f'添加成功：{result}')
            res = ResMsg(data=result)
            responseData = res.to_json()
        else:
            self.usego.sendlog(f'入库失败')
            res = ResMsg(code='B0001', msg=f'入库失败')
            responseData = res.to_json()

        return responseData

    def splicing_submit_push(self):
        """
                    @Datetime ： 2024/10/21 00:28
                    @Author ：eblis
                    @Motto：Amazon SQS 不能接收 过长 消息，大量执行，查数据库 放在脚本上，不能从队列传送
                """
        data_request = request.json
        title_alt = data_request['title_alt']
        alt_text = data_request['alt_text']
        stacking_min = data_request['stacking_min']
        stacking_max = data_request['stacking_max']
        genre = data_request['genre']
        platform = data_request['platform']
        postingStyle = data_request['postingStyle']
        group = data_request['group']
        sort = data_request['sort']
        isarts = data_request['isarts']

        self.usego.sendlog(
            f"接收到的参数：{genre}, {platform}, {stacking_min}, {stacking_max}, {alt_text}, {sort}, {postingStyle}, {isarts}")

        self.usego.sendlog("第一步，先查数据库，查看是否存在符合条件的PC")
        # state=3 是 实际查询为 state !=2

        sql_data = self.ssql.pcSettings_select_sql(platform=platform, state=3)

        if "sql 语句异常" in str(sql_data):
            self.usego.sendlog(f'没有可用的客户端：{sql_data}')
            res = ResMsg(code='B0001', msg=f'没有可用的客户端')
            return res.to_json()

        try:
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
        except Exception as e:
            self.usego.sendlog(f'没有可用的客户端：{e}')
            res = ResMsg(code='B0001', msg=f'没有可用的客户端')
            return res.to_json()

        if not resdatas:
            self.usego.sendlog(f'没有可用的客户端{resdatas}')
            res = ResMsg(code='B0001', msg=f'没有可用的客户端')
            return res.to_json()

        self.usego.sendlog(f'有 {len(resdatas)} 设备符合')

        results = []
        query = {
            "genre": str(genre),
            "platform": str(platform),
            "sort": str(sort),
        }
        total = self.mossql.splicing_interim_find_count("seo_external_links_post", query)
        self.usego.sendlog(f'第二步，本次任务一共需要执行{total} 连接')
        if total == 0:
            self.usego.sendlog(f'没有符合执行条件的数据')
            res = ResMsg(code='B0001', msg=f'没有符合执行条件的数据')
            return res.to_json()

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
                    'genre': genre,
                    'platform': platform,
                    'stacking_min': stacking_min,
                    'stacking_max': stacking_max,
                    'title_alt': title_alt,
                    'alt_text': alt_text,
                    'sort': sort,
                    'isarts': isarts,
                    'postingStyle': postingStyle,
                    'group': group,
                    'start': start,
                    'end': end
                }
                self.usego.sendlog(f' run_{platform}_selenium，任务信息:{task_data}')
                response = self.aws_sqs.sendMSG(queue_url, f"run_{platform}_group", f"run_{platform}_selenium",
                                                task_data)
                result[f"{client}"] = response
                results.append(result)
                self.usego.sendlog(f' run_{platform}_selenium，任务发送结果:{response}')
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
                'genre': genre,
                'platform': platform,
                'stacking_min': stacking_min,
                'stacking_max': stacking_max,
                'title_alt': title_alt,
                'alt_text': alt_text,
                'sort': sort,
                'isarts': isarts,
                'postingStyle': postingStyle,
                'group': group,
                'start': start,
                'end': end
            }
            self.usego.sendlog(f' run_{platform}_selenium，任务信息:{task_data}')
            response = self.aws_sqs.sendMSG(queue_url, f"run_{platform}_group", f"run_{platform}_selenium", task_data)
            # 将 执行pc 状态 修改
            sql_data = self.ssql.pcSettings_update_state_sql(client["name"], state=1)
            self.usego.sendlog(f"pc执行结果{sql_data}")

            result[f"{client}"] = response
            results.append(result)
            self.usego.sendlog(f' run_{platform}_selenium，任务发送结果:{response}')


        res = ResMsg(data=results) if results else ResMsg(code='B0001', msg='No results received')
        return res.to_json()




    def splicing_total(self):
        """
            @Datetime ： 2024/10/28 16:50
            @Author ：eblis
            @Motto：简单描述用途
        """
        try:
            query = {}

            sql_data = self.mossql.splicing_interim_find_count("seo_external_links_post", query)
        except Exception as e:
            self.usego.sendlog(f'list查询失败：{e}')
            sql_data = 0


        self.usego.sendlog(f'查询结果：{sql_data}')
        datas = {
            "total": sql_data,
        }
        res = ResMsg(data=datas)
        return res.to_json()


    def splicing_delete_all(self):
        sql_data = self.mossql.splicing_interim_delet("seo_external_links_post", query=None, multiple=False, clear_all=True)
        self.usego.sendlog(f'删除结果：{sql_data}')
        res = ResMsg(data=sql_data)
        return res.to_json()
    
    
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
    















