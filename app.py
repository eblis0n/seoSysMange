from flask import Flask
from datetime import datetime
import config
import middleware.public.configurationCall as configCall
from flask_cors import CORS
from middleware.public.logs import log_config
from werkzeug.middleware.proxy_fix import ProxyFix
from flask.logging import default_handler
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_session import Session
from datetime import timedelta
from flask_socketio import SocketIO
import threading
from backendServices.src.awsMQ.amazonSQS import amazonSQS
import yaml
import importlib
import time

# 接口蓝图配置
from src.api.sysUserManagement.sys_user_manage import userService
from src.api.sysMenuManagement.sys_menu_manage import menuDeploy
from src.api.pcSettingsManagement.pc_settings_manage import pcManage
from src.api.uploadFileManagement.upload_file_manage import uploadFileManage
from src.api.splicingManagement.splicing_manage import splicingManage
from src.api.publicManagement.public_manage import publicManage




app = Flask(__name__)

#################################################### 跨域 ###########################################################

CORS(app, resources={r"/*": {"origins": eval(configCall.crossDomain)}})
# CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/api/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "https://ilcin.online"}})

# 初始化 SocketIO，使用 eventlet 作为异步消息队列处理程序
socketio = SocketIO(app, async_mode='eventlet')


#################################################### 配置 ###########################################################

# 自动生成接口文件
swagger = Swagger(app)
# 绑定配置文件
app.config.from_object(config)
app.wsgi_app = ProxyFix(app.wsgi_app)
# app.config['SIGNALS_ENABLED'] = False
log_config(configCall.log_folder_path, configCall.log_folder_name, configCall.log_level)
app.logger.removeHandler(default_handler)


# token验证
app.config['JWT_SECRET_KEY'] = configCall.jwt_secret_key  # 用于JWT的秘钥
app.config['SESSION_TYPE'] = 'filesystem'  # session的存储类型，这里使用文件系统
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(configCall.expires_minutes))  # JWT过期时间，这里设置为15分钟

jwt = JWTManager(app)
sess = Session(app)



#################################################### 蓝图 ###########################################################

userService_bp = userService().bp
menuDeploy_bp = menuDeploy().bp
pcManage_bp = pcManage().bp
uploadFile_bp = uploadFileManage().bp
splicing_bp = splicingManage().bp
public_bp = publicManage().bp
#################################################### 引用 ###########################################################



app.register_blueprint(userService_bp)
app.register_blueprint(menuDeploy_bp)
app.register_blueprint(pcManage_bp)
app.register_blueprint(uploadFile_bp)
app.register_blueprint(splicing_bp)
app.register_blueprint(public_bp)






@app.route('/')
def hello_world():  # put application's code here
    mytime = datetime.now()
    return f'访问成功,现在的时间是:{mytime}'



def load_commands():
    with open(f'{configCall.task_address}/commands.yaml', 'r') as file:
        return yaml.safe_load(file)['commands']

def execute_command(command, message):
    module = importlib.import_module(command['module'])
    class_ = getattr(module, command['class'])
    instance = class_()
    method = getattr(instance, command['method'])
    params = [message.get(param) for param in command['params']]
    return method(*params)

def run_sqs_client():
    """
    运行SQS客户端模式,接收任务并执行
    """
    aws_sqs = amazonSQS()
    commands = load_commands()
    
    # 获取当前客户端的ID
    client_id = configCall.client_id
    
    while True:
        # 获取或创建队列URL
        queue_url = aws_sqs.initialization(f'client_{client_id}')['QueueUrl']
        
        # 接收消息
        message = aws_sqs.receive_result(queue_url)
        print(f"接收到 执行命令：{message}")
        if message:
            try:
                # 查找匹配的命令
                command = next((cmd for cmd in commands if cmd['name'] == message.get('command')), None)
                if command:
                    # 执行命令
                    result = execute_command(command, message)
                    # 发送结果
                    aws_sqs.send_task(queue_url, {'result': result})
                else:
                    raise ValueError(f"Unknown command: {message.get('command')}")
            except Exception as e:
                # 发送错误信息
                aws_sqs.send_task(queue_url, {'error': str(e)})
            finally:
                # 删除队列
                aws_sqs.delFIFO(queue_url)
        else:
            # 如果没有消息，等待一段时间再次检查
            time.sleep(10)

if __name__ == '__main__':
    if configCall.isClient == '0':
        print("启动SQS客户端模式")
        # 启动SQS客户端模式
        threading.Thread(target=run_sqs_client, daemon=True).start()
        print("SQS client mode started.")
    
    app.run(host='0.0.0.0', port=int(configCall.flaskport), debug=True)
    # socketio.run(app, host='0.0.0.0', port=int(configCall.flaskport), debug=True)
