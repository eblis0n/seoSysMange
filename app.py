from datetime import datetime, timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session
from flask_socketio import SocketIO
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix
from flask.logging import default_handler
import config
import threading

# 自定义中间件导入
import middleware.public.configurationCall as configCall
from middleware.public.commonUse import otherUse
from middleware.public.logs import log_config
from middleware.control.amazonRun import amazonRun

# API 蓝图导入
from src.api.basis.amazonManagement.amazon_management import amazonManage
from src.api.basis.bloggerManagement.blogger_management import bloggerManage
from src.api.basis.operationsManagement.operations_manage import operationsManage

from src.api.basis.outcomeManagement.outcome_manage import outcomeManage
from src.api.basis.pcSettingsManagement.pc_settings_manage import pcManage
from src.api.basis.publicManagement.public_manage import publicManage
from src.api.basis.splicingManagement.splicing_manage import splicingManage
from src.api.basis.sysMenuManagement.sys_menu_manage import menuDeploy
from src.api.basis.sysUserManagement.sys_user_manage import userService
from src.api.basis.uploadFileManagement.upload_file_manage import uploadFileManage
from src.api.basis.scriptTemplateManagement.script_template_manage import scriptTemplateManage
from src.api.basis.noteManagement.note_info_manegement import noteInfoManage

def create_app():
    """
    创建并配置 Flask 应用
    """
    app = Flask(__name__)
    
    # 基础配置
    _configure_basics(app)
    
    # 配置组件
    socketio = _configure_components(app)
    
    # 注册蓝图
    _register_blueprints(app)
    
    # 配置 Amazon SQS 客户端
    _configure_amazon_sqs()
    
    return app

def _configure_basics(app):
    """配置基本设置"""
    app.config.from_object(config)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    with app.app_context():
        # 配置日志
        logger = log_config(
            configCall.log_folder_path,
            configCall.log_folder_name,
            configCall.log_level
        )
        app.logger.removeHandler(default_handler)

def _configure_components(app):
    """配置应用组件"""
    # CORS
    CORS(app, resources={r"/*": {"origins": eval(configCall.crossDomain)}})
    
    # Socket.IO
    socketio = SocketIO(app, async_mode='eventlet')
    
    # Swagger
    Swagger(app)
    
    # JWT
    app.config.update(
        JWT_SECRET_KEY=configCall.jwt_secret_key,
        SESSION_TYPE='filesystem',
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=int(configCall.expires_minutes))
    )
    JWTManager(app)
    Session(app)
    
    # 通用工具类
    common_use = otherUse()
    common_use.init_app(app)
    
    return socketio

def _register_blueprints(app):
    """注册所有蓝图"""
    blueprints = [
        userService().bp,
        menuDeploy().bp,
        pcManage().bp,
        uploadFileManage().bp,
        splicingManage().bp,
        publicManage().bp,
        amazonManage().bp,
        outcomeManage().bp,
        bloggerManage().bp,
        operationsManage().bp,
        scriptTemplateManage().bp,
        noteInfoManage().bp,
    ]
    
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def _configure_amazon_sqs():
    """配置 Amazon SQS 客户端"""
    if configCall.isClient == '0':
        ama = amazonRun()
        threading.Thread(target=ama.run_sqs_client, daemon=True).start()
        print("SQS client mode started.")

app = create_app()

@app.route('/')
def hello_world():
    """健康检查端点"""
    return f'访问成功,现在的时间是:{datetime.now()}'

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(configCall.flaskport),
        debug=True
    )
