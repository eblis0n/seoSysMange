import os
import sys
import time

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
        policy_document = eval(configCall.aws_policy_document)
        policy_string = json.dumps(policy_document)

        while True:
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
                    print(f"Queue '{queue_name}' was recently deleted. Waiting 60 seconds before retrying...")
                    time.sleep(60)  # 等待 60 秒后重试
                else:
                    print(f"Unexpected error: {e}")
                    raise

    def sendMSG(self, queue_url, msg_group, scriptname, task_data):
        message_body = {"command": f"{scriptname}", "script": task_data}
        response = self.sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_body),
                                         MessageGroupId=msg_group)
        return response

    def takeMSG(self, queue_url, wait_time=20):
        response = self.sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            VisibilityTimeout=30,
            WaitTimeSeconds=wait_time
        )

        if 'Messages' in response:
            message = response['Messages'][0]
            message_body = json.loads(message['Body'])
            receipt_handle = message['ReceiptHandle']

            self.delFIFO(queue_url, receipt_handle)

            return message_body
        return None


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
