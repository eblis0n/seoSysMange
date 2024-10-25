# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/10/25 15:09
@Author ： eblis
@File ：gRPC_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys
import grpc
from concurrent import futures
import time
from google.protobuf import empty_pb2
import task_pb2
import task_pb2_grpc

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

from middleware.dataBaseGO.mongo_sqlCollenction import mongo_sqlGO
from middleware.public.commonUse import otherUse

class TaskScheduler(task_pb2_grpc.TaskSchedulerServicer):
    def __init__(self):
        self.mossql = mongo_sqlGO()
        self.usego = otherUse()

    def DistributeTask(self, request, context):
        # 从请求中获取参数
        stacking_min = request.stacking_min
        stacking_max = request.stacking_max
        alt_tex = request.alt_tex
        platform = request.platform

        # 查找符合条件的客户端
        clients = self.mossql.find_available_clients(platform, state=0)

        if not clients:
            return task_pb2.TaskResponse(success=False, message="No available clients")

        # 获取需要处理的链接
        links = self.mossql.telegra_interim_findAll("seo_external_links_post")

        # 为每个客户端分配任务
        for client in clients:
            # 创建任务
            task = task_pb2.Task(
                client_id=client['id'],
                stacking_min=stacking_min,
                stacking_max=stacking_max,
                alt_tex=alt_tex,
                links=links
            )

            # 这里应该有一个方法来实际发送任务到客户端
            # 例如：self.send_task_to_client(task, client['address'])

            # 更新客户端状态
            self.mossql.update_client_state(client['id'], 1)  # 1 表示正在执行任务

        return task_pb2.TaskResponse(success=True, message="Tasks distributed")

    def ReportTaskCompletion(self, request, context):
        client_id = request.client_id
        success = request.success
        message = request.message

        # 更新任务状态
        if success:
            self.mossql.update_client_state(client_id, 0)  # 0 表示空闲
        else:
            self.mossql.update_client_state(client_id, 2)  # 2 可能表示出错

        # 记录任务完成情况
        self.usego.sendlog(f"Task completion for client {client_id}: Success={success}, Message={message}")

        return empty_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_pb2_grpc.add_TaskSchedulerServicer_to_server(TaskScheduler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
