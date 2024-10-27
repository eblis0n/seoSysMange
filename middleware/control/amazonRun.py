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
from middleware.public.commonUse import otherUse

class amazonRun:
    def __init__(self):
        self.aws_sqs = AmazonSQS()
        self.usego = otherUse()

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

        client_id = configCall.client_id
        is_running = True  # 运行状态标志

        while is_running:
            self.usego.sendlog("等待个60秒再说！！！！")
            time.sleep(60)
            queue_url = self.aws_sqs.initialization(f'client_{client_id}')['QueueUrl']
            message = self.aws_sqs.takeMSG(queue_url)
            self.usego.sendlog(f"{queue_url}, {message}")

            if message:
                try:
                    command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)
                    self.usego.sendlog(f"找到了匹配的{command}")
                    if command:
                        new_message = message.get("script")
                        result = self.execute_command(command, new_message)
                        self.usego.sendlog(f"执行命令result{result}")
                    else:
                        raise ValueError(f"Unknown command: {message.get('command')}")
                except Exception as e:
                    self.usego.sendlog(f"出现异常: {e}")

                finally:
                    self.aws_sqs.delFIFO(queue_url)
            else:
                self.usego.sendlog("没有接收到消息，继续等待...")



if __name__ == '__main__':
    ama = amazonRun()
    ama.run_sqs_client()
