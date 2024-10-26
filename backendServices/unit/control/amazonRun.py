# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/26 16:39
@Author ： eblis
@File ：amazonRun.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import yaml
import importlib
import time
from backendServices.src.awsMQ.amazonSQS import amazonSQS
import middleware.public.configurationCall as configCall

class amazonRun():
    def __init__(self):
        self.aws_sqs = amazonSQS()


    def load_commands(self):
        with open(f'{configCall.task_address}/commands.yaml', 'r+', encoding='utf-8') as file:
            return yaml.safe_load(file)['commands']


    def execute_command(self, command, message):
        module = importlib.import_module(command['module'])
        class_ = getattr(module, command['class'])
        instance = class_()
        method = getattr(instance, command['method'])
        params = [message.get(param) for param in command['params']]
        return method(*params)


    def run_sqs_client(self, ):
        """
        运行SQS客户端模式,接收任务并执行
        """

        commands = self.load_commands()

        # 获取当前客户端的ID
        client_id = configCall.client_id

        while True:
            # 获取或创建队列URL
            queue_url = self.aws_sqs.initialization(f'client_{client_id}')['QueueUrl']

            # 接收消息
            message = self.aws_sqs.receive_result(queue_url)
            print(f"接收到 执行命令：{message}")
            if message:
                try:
                    # 查找匹配的命令
                    command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)
                    if command:
                        # 执行命令
                        result = self.execute_command(command, message)
                        # 发送结果
                        self.aws_sqs.send_task(queue_url, {'result': result})
                    else:
                        raise ValueError(f"Unknown command: {message.get('command')}")
                except Exception as e:
                    # 发送错误信息
                    self.aws_sqs.send_task(queue_url, {'error': str(e)})
                finally:
                    # 删除队列
                    self.aws_sqs.delFIFO(queue_url)
            else:
                # 如果没有消息，等待一段时间再次检查
                time.sleep(10)
