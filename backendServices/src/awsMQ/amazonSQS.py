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
import publicFunctions.configuration as configuration
# AWS 访问密钥和密钥 ID


class amazonSQS():
    def __init__(self):
        # 创建 SQS 客户端
        self.sqs = boto3.client('sqs', region_name=configuration.aws_region_name,
                                aws_access_key_id=configuration.aws_access_key,
                                aws_secret_access_key=configuration.aws_secret_key)

    def initialization(self,taskid):
        """
            @Datetime ： 2024/5/10 10:06
            @Author ：eblis
            @Motto：简单描述用途
        """


        nowdate = datetime.now().strftime("%Y%m%d%H%M%S")
        # 创建或获取 SQS FIFO 队列的 URL
        queue_name = f'SQS-{taskid}-{nowdate}.fifo'
        policy_document = eval(configuration.aws_policy_document)
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
    def send(self, queue_url, datas):
        """
            @Datetime ： 2024/5/10 10:32
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 发送消息到 FIFO 队列

        message_body = {"command": "execute_script", "script": datas }
        message_group_id = 'group1'
        response = self.sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_body),
                                    MessageGroupId=message_group_id)
        # print(f"Sent message to FIFO queue: {json.dumps(message_body)}")
        return response

    def takeMSG(self,queue_url):
        """
            @Datetime ： 2024/5/10 10:38
            @Author ：eblis
            @Motto：简单描述用途
        """
        # 接收消息
        response = self.sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            VisibilityTimeout=30,
            WaitTimeSeconds=20
        )

        if 'Messages' in response:
            message = response['Messages'][0]
            message_body = json.loads(message['Body'])

            # 解析消息内容
            command = message_body.get('command')
            script = message_body.get('script')

            # 执行命令
            if command == 'execute_script':
                exec(script)

            # 删除已处理的消息
            receipt_handle = message['ReceiptHandle']
            self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
        else:
            print("No messages in the queue")
# 删除 FIFO 队列
    def delFIFO(self, queue_url):
        """
            @Datetime ： 2024/5/10 10:39
            @Author ：eblis
            @Motto：简单描述用途
        """
        self.sqs.delete_queue(QueueUrl=queue_url)
        print("FIFO queue deleted")


    def delete_message(self, queue_url, receipt_handle,):
        response = self.sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )
        print(response)



if __name__ == '__main__':
    aws = amazonSQS()
    response = aws.initialization(79)
    queue_url = response['QueueUrl']

    print("queue_url", queue_url)
    # 第二步 发送
    msg = "print(\'Hello World\')"
    aws.send(queue_url, msg)
    # 第三步 接收
    aws.takeMSG(queue_url)
    fifodd = ['SQS-79-20240615165829.fifo','SQS-79-20240615165839.fifo','SQS-79-20240615165848.fifo','SQS-79-20240615165855.fifo']
    for ff in fifodd:
        queue_url = f"https://sqs.us-east-1.amazonaws.com/151205356403/{ff}"
        aws.delFIFO(queue_url)