# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/18 22:16
@Author ： eblis
@File ：add_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

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
        is_running = True

        while is_running:
            self.usego.sendlog("等待 60 秒再说...")
            time.sleep(60)

            try:
                queue_url = self.aws_sqs.initialization(f'client_{client_id}')['QueueUrl']
                message_result = self.aws_sqs.takeMSG(queue_url)

                if message_result:
                    message = message_result.get('message')
                    receipt_handle = message_result.get('receipt_handle')

                    self.usego.sendlog(f"接收到消息: {message}")
                    command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)

                    if command:
                        command["script"]["receipt_handle"] = receipt_handle
                        try:
                            self.usego.sendlog(f"开始执行命令: {command}")
                            new_message = message.get("script")
                            result = self.execute_command(command, new_message)

                            if result:  # 只有在任务成功执行后才删除消息
                                self.usego.sendlog(f"命令执行成功: {result}")
                                if receipt_handle:
                                    self.aws_sqs.deleteMSG(queue_url, receipt_handle)
                                    self.usego.sendlog(f"消息已删除: {receipt_handle}")
                            else:
                                self.usego.sendlog("命令执行失败，保留消息以便重试")

                        except Exception as e:
                            self.usego.sendlog(f"命令执行出错: {e}")
                            # 不删除消息，允许后续重试
                    else:
                        self.usego.sendlog(f"未找到匹配的命令: {message.get('command')}")
                else:
                    self.usego.sendlog("没有接收到消息，继续等待...")

            except Exception as e:
                self.usego.sendlog(f"处理消息时出错: {e}")

if __name__ == '__main__':
    ama = amazonRun()
    ama.run_sqs_client()
