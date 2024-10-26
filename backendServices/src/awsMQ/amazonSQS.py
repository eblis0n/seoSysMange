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
import time
import logging
import middleware.public.configurationCall as configCall

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import boto3
from botocore.exceptions import ClientError, SSLError
from botocore.config import Config
import json
from middleware.public.commonUse import otherUse

class amazonSQS():
    def __init__(self):
        self.usego = otherUse()
        self.max_retries = 3
        self.retry_delay = 1  # 秒
        
        config = Config(
            region_name=configCall.aws_region_name,
            signature_version='v4',
            retries={
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
        
        self.sqs = boto3.client('sqs', 
                                region_name=configCall.aws_region_name,
                                aws_access_key_id=configCall.aws_access_key,
                                aws_secret_access_key=configCall.aws_secret_key,
                                config=config,
                                verify=True)


    def initialization(self, taskid):
        queue_name = f'SQS-{taskid}.fifo'
        logger.debug(f"Initializing SQS FIFO queue: {queue_name}")
        policy_document = eval(configCall.aws_policy_document)
        policy_string = json.dumps(policy_document)

        queue_attributes = {
            'FifoQueue': 'true',
            "DelaySeconds": "0",
            "VisibilityTimeout": "60",
            'ContentBasedDeduplication': 'true',
            'Policy': policy_string
        }

        for attempt in range(self.max_retries):
            try:
                # 首先尝试获取现有队列
                existing_queues = self.sqs.list_queues(QueueNamePrefix=queue_name)
                if 'QueueUrls' in existing_queues and existing_queues['QueueUrls']:
                    queue_url = existing_queues['QueueUrls'][0]
                    logger.debug(f"Queue already exists: {queue_url}")
                    
                    # 更新现有队列的属性
                    self.sqs.set_queue_attributes(
                        QueueUrl=queue_url,
                        Attributes=queue_attributes
                    )
                    logger.debug("Queue attributes updated successfully")
                else:
                    # 如果队列不存在，创建新队列
                    response = self.sqs.create_queue(
                        QueueName=queue_name,
                        Attributes=queue_attributes
                    )
                    queue_url = response['QueueUrl']
                    logger.debug(f"New queue created: {queue_url}")

                return {'QueueUrl': queue_url}

            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to initialize queue after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def send_task(self, queue_url, task_data):
        self.usego.sendlog(f"Attempting to send message to queue: {queue_url}")
        for attempt in range(self.max_retries):
            try:
                response = self.sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(task_data),
                    MessageGroupId='task_group'
                )
                self.usego.sendlog("Message sent successfully")
                return response
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to send message after {self.max_retries} attempts: {str(e)}")
                    raise
                self.usego.sendlog(f"Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def receive_result(self, queue_url, wait_time=20):
        self.usego.sendlog(f"Attempting to receive message from queue: {queue_url}")
        for attempt in range(self.max_retries):
            try:
                response = self.sqs.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=wait_time
                )

                if 'Messages' in response:
                    message = response['Messages'][0]
                    result = json.loads(message['Body'])
                    receipt_handle = message['ReceiptHandle']

                    self.sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=receipt_handle
                    )
                    self.usego.sendlog("Message received and deleted successfully")
                    return result
                self.usego.sendlog("No messages in queue")
                return None
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to receive message after {self.max_retries} attempts: {str(e)}")
                    raise
                self.usego.sendlog(f"Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def delFIFO(self, queue_url):
        self.usego.sendlog(f"Attempting to delete queue: {queue_url}")
        for attempt in range(self.max_retries):
            try:
                self.sqs.delete_queue(QueueUrl=queue_url)
                self.usego.sendlog("Queue deleted successfully")
                return
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to delete queue after {self.max_retries} attempts: {str(e)}")
                    raise
                self.usego.sendlog(f"Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

if __name__ == '__main__':
    pass
