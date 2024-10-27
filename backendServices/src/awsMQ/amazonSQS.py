# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/19 13:37
@Author ： eblis
@File ：mongoDataBase.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import time

# 设置项目根目录
base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import boto3
import json
from botocore.exceptions import ClientError
from middleware.public.commonUse import otherUse
import middleware.public.configurationCall as configCall

class AmazonSQS:

    def __init__(self):
        self.usego = otherUse()
        self.sqs = boto3.client('sqs', region_name=configCall.aws_region_name,
                                aws_access_key_id=configCall.aws_access_key,
                                aws_secret_access_key=configCall.aws_secret_key)

    def list_queues(self, queue_name_prefix=None):
        """
        列出所有 SQS 队列，支持根据前缀筛选。

        :param queue_name_prefix: 可选，队列名称前缀，用于筛选
        :return: 队列 URL 列表
        """
        try:
            if queue_name_prefix:
                response = self.sqs.list_queues(QueueNamePrefix=queue_name_prefix)
            else:
                response = self.sqs.list_queues()

            return response

        except ClientError as e:
            self.usego.sendlog(f"Failed to list queues: {e}")
            return []



    def initialization(self, taskid):
        queue_name = f'SQS-{taskid}.fifo'
        policy_document = json.loads(configCall.aws_policy_document)  # 使用 json.loads
        policy_string = json.dumps(policy_document)

        # 尝试列出现有队列
        try:
            response = self.list_queues(queue_name)  # 使用 list_queues 方法
            queues = response.get('QueueUrls', [])
            if queues:
                self.usego.sendlog(f"Queue {queue_name} already exists. Using the existing queue...")
                return {'QueueUrl': queues[0]}  # 返回第一个找到的队列 URL

        except ClientError as e:
            self.usego.sendlog(f"Failed to list queues: {e}")

        self.usego.sendlog(f"避免翻车，等个60秒比较好")
        time.sleep(60)



        # 如果队列不存在，则创建新队列
        retries = 3  # 设置重试次数
        for attempt in range(retries):
            try:
                response = self.sqs.create_queue(
                    QueueName=queue_name,
                    Attributes={
                        'FifoQueue': 'true',
                        "DelaySeconds": "0",
                        "VisibilityTimeout": "60",
                        'ContentBasedDeduplication': 'true',
                        'Policy': policy_string
                    }
                )
                return response

            except ClientError as e:
                if e.response['Error']['Code'] == 'QueueDeletedRecently':
                    if attempt < retries - 1:
                        self.usego.sendlog(
                            f"Queue '{queue_name}' was recently deleted. Waiting 60 seconds before retrying...")
                        time.sleep(60)  # 等待 60 秒后重试
                    else:
                        self.usego.sendlog(f"Exceeded maximum retries for '{queue_name}'.")
                        raise
                else:
                    self.usego.sendlog(f"Unexpected error: {e}")
                    raise

    def sendMSG(self, queue_url, msg_group, scriptname, task_data, retries=3, delay=5):
        message_body = {"command": f"{scriptname}", "script": task_data}

        for attempt in range(retries):
            try:
                response = self.sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(message_body),
                    MessageGroupId=msg_group
                )
                return response
            except ClientError as e:
                self.usego.sendlog(f"Attempt {attempt + 1} to send message failed: {e}")
                time.sleep(delay)  # 等待一段时间后重试
                if attempt == retries - 1:
                    raise  # 如果重试次数用尽，则抛出异常

    def takeMSG(self, queue_url, wait_time=20, retries=3, delay=5):
        for attempt in range(retries):
            try:
                response = self.sqs.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    VisibilityTimeout=30,
                    WaitTimeSeconds=wait_time
                )

                if 'Messages' in response:
                    message = response['Messages'][0]
                    message_body = json.loads(message['Body'])
                    return message_body
                else:
                    self.usego.sendlog("No messages received.")
                    return None

            except ClientError as e:
                self.usego.sendlog(f"Attempt {attempt + 1} to receive message failed: {e}")
                time.sleep(delay)  # 等待一段时间后重试
                if attempt == retries - 1:
                    raise  # 如果重试次数用尽，则抛出异常

    def delFIFO(self, queue_url, receipt_handle=None):
        if receipt_handle is None:
            self.sqs.delete_queue(QueueUrl=queue_url)
            self.usego.sendlog("FIFO queue deleted")
        else:
            response = self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )
            self.usego.sendlog(f"删除结果{response}")


if __name__ == '__main__':
    aws = AmazonSQS()
    response = aws.list_queues()
    queues = response.get('QueueUrls', [])
    if queues:
        print("123")
    else:
        print(456)
    # response = aws.initialization("client_this_mac_1_not")
    # queue_url = response['QueueUrl']
    # print("queue_url", queue_url)
    #
    # # msg = "print('Hello World')"
    # # aws.sendMSG(queue_url, "testgroup", "execute_script", msg)
    #
    # # 假设已经初始化了 SQS 客户端并获取了 queue_url
    # task_data = {
    #     'command': 'test1',  # 指定要执行的命令
    # }
    #
    # msg_group = "test1"  # 消息分组
    # scriptname = "test1"  # 脚本名称
    #
    # # 发送消息到 SQS 队列
    # response = aws.sendMSG(queue_url, msg_group, scriptname, task_data)
    #
    # # 打印响应（可选）
    # print("Message sent:", response)
