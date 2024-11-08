import os
import sys
import time
import json
import boto3
from botocore.exceptions import ClientError
from middleware.public.commonUse import otherUse
import middleware.public.configurationCall as configCall

class AmazonSQS:

    def __init__(self):
        self.usego = otherUse()

    def _get_sqs_client(self):
        """每次调用都创建一个新的 SQS 客户端"""
        return boto3.client('sqs', region_name=configCall.aws_region_name,
                            aws_access_key_id=configCall.aws_access_key,
                            aws_secret_access_key=configCall.aws_secret_key)

    def list_queues(self, queue_name_prefix=None):
        """
        列出所有 SQS 队列，支持根据前缀筛选。

        :param queue_name_prefix: 可选，队列名称前缀，用于筛选
        :return: 队列 URL 列表
        """
        sqs = self._get_sqs_client()  # 获取新的 SQS 客户端
        try:
            if queue_name_prefix:
                response = sqs.list_queues(QueueNamePrefix=queue_name_prefix)
            else:
                response = sqs.list_queues()

            return response

        except ClientError as e:
            self.usego.sendlog(f"Failed to list queues: {e}")
            return []

    def initialization(self, taskid):
        queue_name = f'SQS-{taskid}.fifo'
        sqs = self._get_sqs_client()  # 获取新的 SQS 客户端
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
                response = sqs.create_queue(
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
        sqs = self._get_sqs_client()
        message_body = {"command": f"{scriptname}", "script": task_data}

        for attempt in range(retries):
            try:
                response = sqs.send_message(
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

    def takeMSG(self, queue_url):
        """
        接收消息并返回消息内容和接收句柄
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )
            
            if 'Messages' in response:
                message = response['Messages'][0]
                return {
                    'message': json.loads(message['Body']),
                    'receipt_handle': message['ReceiptHandle']
                }
            return None
        except Exception as e:
            print(f"接收消息时出错: {e}")
            return None

    def deleteMSG(self, queue_url, receipt_handle):
        """
        删除指定的消息
        """
        try:
            self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except Exception as e:
            print(f"删除消息时出错: {e}")
            return False

    def delFIFO(self, queue_url, receipt_handle=None):
        """
        删除 FIFO 队列或消息
        """
        sqs = self._get_sqs_client()
        try:
            if receipt_handle is None:
                # 删除整个队列
                self.usego.sendlog(f"Deleting the FIFO queue: {queue_url}")
                sqs.delete_queue(QueueUrl=queue_url)
                self.usego.sendlog("FIFO queue deleted successfully.")
            else:
                # 删除消息
                response = sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle,
                )
                self.usego.sendlog(f"Message deleted: {response}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'QueueDoesNotExist':
                self.usego.sendlog(f"Queue {queue_url} does not exist.")
            elif error_code == 'QueueDeletedRecently':
                self.usego.sendlog(f"Queue {queue_url} was deleted recently. It cannot be deleted again.")
            else:
                self.usego.sendlog(f"Failed to delete FIFO queue or message: {e}")
                raise  # 抛出异常，保证错误不被忽视

    def has_more_messages(self, queue_url):
        """
        检查队列中是否有更多的消息
        :param queue_url: 队列 URL
        :return: 如果队列中还有消息，则返回 True，否则返回 False
        """
        sqs = self._get_sqs_client()
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            VisibilityTimeout=30,
            WaitTimeSeconds=5  # 设置一个较短的等待时间
        )

        if 'Messages' in response:
            return True  # 如果队列中有消息，返回 True
        return False  # 如果没有消息，返回 False

if __name__ == '__main__':
    aws = AmazonSQS()
    response = aws.list_queues()
    queues = response.get('QueueUrls', [])
    if queues:
        print("Queues found:", queues)
    else:
        print("No queues found.")

    # Example of initializing a queue
    # response = aws.initialization("client_this_mac_1_not")
    # queue_url = response['QueueUrl']
    # print("queue_url", queue_url)

    # Send a message to the queue
    # task_data = {'command': 'test1', 'script': 'print("Hello World")'}
    # msg_group = "test1"
    # scriptname = "test1"
    # response = aws.sendMSG(queue_url, msg_group, scriptname, task_data)
    # print("Message sent:", response)

    # Receive a message from the queue
    # message = aws.takeMSG(queue_url)
    # print("Received message:", message)
