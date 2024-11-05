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
        """加载并返回命令配置"""
        try:
            with open(f'{configCall.task_address}/commands.yaml', 'r+', encoding='utf-8') as file:
                commands = yaml.safe_load(file).get('commands', [])
                return commands
        except Exception as e:
            self.usego.sendlog(f"加载命令文件失败: {e}")
            return []

    def execute_command(self, command, message):
        """动态执行命令"""
        try:
            module = importlib.import_module(command['module'])
            class_ = getattr(module, command['class'])
            instance = class_()
            method = getattr(instance, command['method'])
            params = [message.get(param) for param in command['params']]
            return method(*params)
        except Exception as e:
            self.usego.sendlog(f"执行命令时出错: {e}")
            return str(e)

    def run_sqs_client(self):
        """处理 SQS 消息并执行相应的命令"""
        commands = self.load_commands()
        if not commands:
            self.usego.sendlog("没有加载到任何命令，程序退出。")
            return

        client_id = configCall.client_id
        is_running = True  # 运行状态标志

        while is_running:
            self.usego.sendlog("等待 60 秒再说...")
            time.sleep(60)

            try:
                # 初始化 SQS 客户端并获取队列 URL
                queue_url = self.aws_sqs.initialization(f'client_{client_id}')['QueueUrl']
                message = self.aws_sqs.takeMSG(queue_url)

                if message:
                    self.usego.sendlog(f"接收到消息: {message}")
                    command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)

                    if command:
                        self.usego.sendlog(f"找到了匹配的命令: {command}")
                        new_message = message.get("script")
                        result = self.execute_command(command, new_message)
                        self.usego.sendlog(f"命令执行结果: {result}")
                    else:
                        self.usego.sendlog(f"未找到匹配的命令: {message.get('command')}")
                        raise ValueError(f"未知的命令: {message.get('command')}")
                else:
                    self.usego.sendlog("没有接收到消息，继续等待...")

            except Exception as e:
                self.usego.sendlog(f"处理消息时出错: {e}")

if __name__ == '__main__':
    ama = amazonRun()
    ama.run_sqs_client()
