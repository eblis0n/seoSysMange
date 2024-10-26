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
from backendServices.src.awsMQ.amazonSQS import AmazonSQS
import middleware.public.configurationCall as configCall

class amazonRun:
    def __init__(self):
        self.aws_sqs = AmazonSQS()

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

    def run_sqs_client(self):
        commands = self.load_commands()
        # print("commands", commands)
        client_id = configCall.client_id
        is_running = True  # 运行状态标志

        while is_running:
            queue_url = self.aws_sqs.initialization(f'client_{client_id}')['QueueUrl']
            message = self.aws_sqs.takeMSG(queue_url)
            print(f"{queue_url}, {message}")

            if message:
                try:
                    command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)
                    # print(f"找到了匹配的{command}")
                    if command:
                        result = self.execute_command(command, message)
                        print("执行命令result", result)
                    else:
                        raise ValueError(f"Unknown command: {message.get('command')}")
                except Exception as e:
                    print(f"出现异常: {e}")
                    # is_running = False  # 设置为 False，停止运行
                finally:
                    self.aws_sqs.delFIFO(queue_url)
                    time.sleep(60)

            else:
                print("没有接收到消息，继续等待...")
                time.sleep(60)


if __name__ == '__main__':
    ama = amazonRun()
    ama.run_sqs_client()
