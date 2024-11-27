import json
import re
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

    def _handle_error(self, error_message: str, exception: Exception, fallback_value=None):
        """统一的错误处理函数"""
        self.usego.sendlog(f"{error_message}: {exception}")
        return fallback_value

    def list_queues(self, queue_name_prefix=None):
        """列出所有 SQS 队列"""
        try:
            params = {'QueueNamePrefix': queue_name_prefix} if queue_name_prefix else {}
            return self.sqs.list_queues(**params)
        except ClientError as e:
            return self._handle_error("Failed to list queues", e, {'QueueUrls': []})

    def initialization(self, taskid):
        """初始化或获取现有队列"""
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', taskid)

        queue_name = f'SQS-{sanitized_name}.fifo'


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
            return self._handle_error("Failed to create queue", e)

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
            return self._handle_error("Failed to send message", e)

    def takeMSG(self, queue_url):
        """接收消息"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20  # 使用长轮询减少请求次数
            )

            if messages := response.get('Messages'):
                message = messages[0]
                return {
                    'message': json.loads(message['Body']),
                    'receipt_handle': message['ReceiptHandle']
                }
            return None
        except Exception as e:
            return self._handle_error("Failed to receive message", e)

    def deleteMSG(self, queue_url, receipt_handle=None):
        """删除指定消息或一条消息（如果未提供 receipt_handle）"""
        try:
            # 删除指定消息
            if receipt_handle:
                self.usego.sendlog(f"Deleting specified message with ReceiptHandle: {receipt_handle}")
                self.sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )
            # 删除一条消息（如果未提供 receipt_handle）
            else:
                self.usego.sendlog(f"Deleting one message from the queue")
                messages = self.sqs.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1
                ).get("Messages", [])

                if messages:
                    self.sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=messages[0]["ReceiptHandle"]
                    )
            return True
        except Exception as e:
            return self._handle_error("Failed to delete message", e, False)

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
            return self._handle_error("Failed to check messages", e, False)


if __name__ == '__main__':
    aws = AmazonSQS()

    # List queues
    response = aws.list_queues()
    queues = response.get('QueueUrls', [])
    if queues:
        print("Queues found:", queues)
    else:
        print("No queues found.")

