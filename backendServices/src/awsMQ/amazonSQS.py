import json
import time
import boto3
from botocore.exceptions import ClientError
from middleware.public.commonUse import otherUse
import middleware.public.configurationCall as configCall

class AmazonSQS:
    def __init__(self):
        self.usego = otherUse()
        self._sqs = None

    @property
    def sqs(self):
        """懒加载 SQS 客户端"""
        if self._sqs is None:
            self._sqs = boto3.client(
                'sqs',
                region_name=configCall.aws_region_name,
                aws_access_key_id=configCall.aws_access_key,
                aws_secret_access_key=configCall.aws_secret_key
            )
        return self._sqs

    def list_queues(self, queue_name_prefix=None):
        """列出所有 SQS 队列"""
        try:
            params = {'QueueNamePrefix': queue_name_prefix} if queue_name_prefix else {}
            return self.sqs.list_queues(**params)
        except ClientError as e:
            self.usego.sendlog(f"Failed to list queues: {e}")
            return {'QueueUrls': []}

    def initialization(self, taskid):
        """初始化或获取现有队列"""
        queue_name = f'SQS-{taskid}.fifo'
        
        # 检查现有队列
        response = self.list_queues(queue_name)
        if queues := response.get('QueueUrls'):
            self.usego.sendlog(f"Using existing queue: {queue_name}")
            return {'QueueUrl': queues[0]}

        # 创建新队列
        self.usego.sendlog("Creating new queue, waiting 60s...")
        time.sleep(60)

        try:
            return self.sqs.create_queue(
                QueueName=queue_name,
                Attributes={
                    'FifoQueue': 'true',
                    'DelaySeconds': '0',
                    'VisibilityTimeout': '60',
                    'ContentBasedDeduplication': 'true',
                    'Policy': json.dumps(json.loads(configCall.aws_policy_document))
                }
            )
        except ClientError as e:
            self.usego.sendlog(f"Failed to create queue: {e}")
            raise

    def sendMSG(self, queue_url, msg_group, scriptname, task_data):
        """发送消息到队列"""
        message_body = {
            "command": scriptname,
            "script": task_data
        }

        try:
            return self.sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body),
                MessageGroupId=msg_group
            )
        except ClientError as e:
            self.usego.sendlog(f"Failed to send message: {e}")
            raise

    def takeMSG(self, queue_url):
        """接收消息"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )
            
            if messages := response.get('Messages'):
                message = messages[0]
                return {
                    'message': json.loads(message['Body']),
                    'receipt_handle': message['ReceiptHandle']
                }
            return None
        except Exception as e:
            self.usego.sendlog(f"Failed to receive message: {e}")
            return None

    def deleteMSG(self, queue_url, receipt_handle=None):
        """删除指定消息或一条消息（如果未提供 receipt_handle）"""

        try:
            if receipt_handle:
                self.usego.sendlog(f"删除指定的单条消息")
                # 删除指定的单条消息
                self.sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )
            else:
                # 获取一条消息
                self.usego.sendlog(f"删除一条信息")
                messages = self.sqs.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1  # 只获取一条消息
                ).get("Messages", [])

                # 删除获取到的消息（如果存在）
                if messages:
                    self.sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=messages[0]["ReceiptHandle"]
                    )

            return True

        except Exception as e:
            self.usego.sendlog(f"Failed to delete message: {e}")
            return False

    def has_messages(self, queue_url):
        """检查队列是否有消息"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                VisibilityTimeout=30,
                WaitTimeSeconds=5
            )
            return 'Messages' in response
        except Exception as e:
            self.usego.sendlog(f"Failed to check messages: {e}")
            return False

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
