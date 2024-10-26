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

import middleware.public.configurationCall as configCall
class AmazonSQS:

    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=configCall.aws_region_name,
                                aws_access_key_id=configCall.aws_access_key,
                                aws_secret_access_key=configCall.aws_secret_key)

    def initialization(self, taskid):
        queue_name = f'SQS-{taskid}.fifo'
        policy_document = json.loads(configCall.aws_policy_document)  # 使用 json.loads
        policy_string = json.dumps(policy_document)

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
                if e.response['Error']['Code'] == 'QueueAlreadyExists':
                    print(f"Queue {queue_name} already exists. Retrieving its URL...")
                    return self.sqs.get_queue_url(QueueName=queue_name)
                elif e.response['Error']['Code'] == 'QueueDeletedRecently':
                    if attempt < retries - 1:
                        print(f"Queue '{queue_name}' was recently deleted. Waiting 60 seconds before retrying...")
                        time.sleep(60)  # 等待 60 秒后重试
                    else:
                        print(f"Exceeded maximum retries for '{queue_name}'.")
                        raise
                else:
                    print(f"Unexpected error: {e}")
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
                print(f"Attempt {attempt + 1} to send message failed: {e}")
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
                    print("No messages received.")
                    return None

            except ClientError as e:
                print(f"Attempt {attempt + 1} to receive message failed: {e}")
                time.sleep(delay)  # 等待一段时间后重试
                if attempt == retries - 1:
                    raise  # 如果重试次数用尽，则抛出异常

    def delFIFO(self, queue_url, receipt_handle=None):
        if receipt_handle is None:
            self.sqs.delete_queue(QueueUrl=queue_url)
            print("FIFO queue deleted")
        else:
            response = self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )
            print(response)


if __name__ == '__main__':
    aws = AmazonSQS()
    response = aws.initialization("client_this_mac_1_not")
    queue_url = response['QueueUrl']
    print("queue_url", queue_url)

    # msg = "print('Hello World')"
    # aws.sendMSG(queue_url, "testgroup", "execute_script", msg)

    # 假设已经初始化了 SQS 客户端并获取了 queue_url
    task_data = {
        'command': 'test1',  # 指定要执行的命令
    }

    msg_group = "test1"  # 消息分组
    scriptname = "test1"  # 脚本名称

    # 发送消息到 SQS 队列
    response = aws.sendMSG(queue_url, msg_group, scriptname, task_data)

    # 打印响应（可选）
    print("Message sent:", response)
