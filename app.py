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


# 接口蓝图配置
from src.api.sysUserManagement.sys_user_manage import userService
from src.api.sysMenuManagement.sys_menu_manage import menuDeploy
from src.api.pcSettingsManagement.pc_settings_manage import pcManage
from src.api.uploadFileManagement.upload_file_manage import uploadFileManage
from src.api.telegraManagement.telegra_manage import telegraManage




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
telegra_bp = telegraManage().bp

#################################################### 引用 ###########################################################



app.register_blueprint(userService_bp)
app.register_blueprint(menuDeploy_bp)
app.register_blueprint(pcManage_bp)
app.register_blueprint(uploadFile_bp)
app.register_blueprint(telegra_bp)






@app.route('/')
def hello_world():  # put application's code here
    mytime = datetime.now()
    return f'访问成功,现在的时间是:{mytime}'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(configCall.flaskport), debug=True)
    # socketio.run(app, host='0.0.0.0', port=int(configCall.flaskport), debug=True)
