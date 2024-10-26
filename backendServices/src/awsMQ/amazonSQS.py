# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/5/9 17:40
@Author ： eblis
@File ：amazonSQS.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
from datetime import datetime

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
import boto3
import json

import middleware.public.configurationCall as configCall


# AWS 访问密钥和密钥 ID


class amazonSQS():
    def __init__(self):
        # 创建 SQS 客户端
        self.sqs = boto3.client('sqs', region_name=configCall.aws_region_name,
                                aws_access_key_id=configCall.aws_access_key,
                                aws_secret_access_key=configCall.aws_secret_key)

    def initialization(self, taskid):
        """
            @Datetime ： 2024/5/10 10:06
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 创建或获取 SQS FIFO 队列的 URL
        queue_name = f'SQS-{taskid}.fifo'
        print(f"SQS FIFO 队列的 名称:{queue_name}")
        policy_document = eval(configCall.aws_policy_document)
        policy_string = json.dumps(policy_document)

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

    #

    def delete_message(self, queue_url, receipt_handle=None):
        """
            @Datetime ： 2024/5/10 10:39
            @Author ：eblis
            @Motto：删除 FIFO 队列
        """
        if receipt_handle is None:
            response = self.sqs.delete_message(
                QueueUrl=queue_url
            )
        else:
            response = self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )
        return response

    def send_task(self, queue_url, task_data):
        """
        发送任务到指定的SQS队列
        """
        message_body = json.dumps(task_data)
        message_group_id = 'task_group'
        response = self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageGroupId=message_group_id
        )
        return response

    def receive_result(self, queue_url, wait_time=20):
        """
        从指定的SQS队列接收结果
        """
        response = self.sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_time
        )

        if 'Messages' in response:
            message = response['Messages'][0]
            result = json.loads(message['Body'])
            receipt_handle = message['ReceiptHandle']

            # 删除已处理的消息
            self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

            return result
        return None


if __name__ == '__main__':
    pass
