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
import time



base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import boto3
from botocore.exceptions import ClientError, SSLError
from botocore.config import Config
import json
from middleware.public.commonUse import otherUse
import middleware.public.configurationCall as configCall

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
        queue_attributes = {
            'FifoQueue': 'true',
            'DelaySeconds': '0',
            'VisibilityTimeout': '60',
            'ContentBasedDeduplication': 'true',
        }


        for attempt in range(self.max_retries):
            try:
                response = self.sqs.create_queue(
                    QueueName=queue_name,
                    Attributes=queue_attributes
                )

                return response
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to send message after {self.max_retries} attempts: {str(e)}")
                    raise
                time.sleep(self.retry_delay)

    def send_task(self, queue_url, task_data):
        for attempt in range(self.max_retries):
            try:
                response = self.sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(task_data),
                    MessageGroupId='task_group'
                )
                return response
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to send message after {self.max_retries} attempts: {str(e)}")
                    raise
                time.sleep(self.retry_delay)

    def receive_result(self, queue_url, wait_time=20):

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

                    return result

                return None
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to send message after {self.max_retries} attempts: {str(e)}")
                    raise

                time.sleep(self.retry_delay)

    def delFIFO(self, queue_url):

        for attempt in range(self.max_retries):
            try:
                self.sqs.delete_queue(QueueUrl=queue_url)

                return
            except (ClientError, SSLError) as e:
                if attempt == self.max_retries - 1:
                    self.usego.sendlog(f"Failed to send message after {self.max_retries} attempts: {str(e)}")
                    raise

                time.sleep(self.retry_delay)

if __name__ == '__main__':
    pass
