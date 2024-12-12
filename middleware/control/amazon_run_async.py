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
import concurrent.futures
from backendServices.src.awsMQ.amazonSQS import AmazonSQS
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse

class AmazonRunAsync:
    def __init__(self):
        self.aws_sqs = AmazonSQS()
        self.usego = otherUse()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)  # 限制并发处理数量

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

    def delete_message(self, queue_url, receipt_handle):
        """删除接收到的消息"""
        try:
            self.aws_sqs.deleteMSG(queue_url, receipt_handle)
            self.usego.sendlog(f"消息已成功删除: {receipt_handle}")
        except Exception as e:
            self.usego.sendlog(f"删除消息时出错: {e}")

    def process_message(self, message, receipt_handle, commands):
        """处理消息逻辑"""
        try:
            command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)

            if command:
                command["script"]["receipt_handle"] = receipt_handle
                self.usego.sendlog(f"开始执行命令: {command}")
                new_message = message.get("script")
                result = self.execute_command(command, new_message)

                if result:  # 只有在任务成功执行后才删除消息
                    self.usego.sendlog(f"命令执行成功: {result}")
                else:
                    self.usego.sendlog("命令执行失败")
            else:
                self.usego.sendlog(f"未找到匹配的命令: {message.get('command')}")
        except Exception as e:
            self.usego.sendlog(f"处理消息时出错: {e}")

    def run(self):
        """主逻辑：接收、删除并异步处理消息"""
        commands = self.load_commands()
        if not commands:
            self.usego.sendlog("没有加载到任何命令，程序退出。")
            return

        client_id = configCall.client_id
        queue_url = self.aws_sqs.initialization(f'client_{client_id}')['QueueUrl']
        self.usego.sendlog(f"使用队列: {queue_url}")

        while True:
            # self.usego.sendlog("避免异常，等待 30 秒再说...")
            # time.sleep(30)
            try:
                message_result = self.aws_sqs.takeMSG(queue_url)

                if message_result:
                    message = message_result.get("message")
                    receipt_handle = message_result.get("receipt_handle")

                    self.usego.sendlog(f"接收到消息: {message}")

                    # 先删除消息
                    self.aws_sqs.deleteMSG(queue_url, receipt_handle)

                    # 异步处理消息
                    self.executor.submit(self.process_message, message, receipt_handle, commands)
                else:
                    self.usego.sendlog("未收到新消息，等待 30 秒")
                    time.sleep(30)
            except Exception as e:
                self.usego.sendlog(f"消息处理循环出错: {e}")

if __name__ == "__main__":
    runner = AmazonRunAsync()
    runner.run()