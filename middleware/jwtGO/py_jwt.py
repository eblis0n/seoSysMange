# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/29 21:25
@Author ： eblis
@File ：py_jwt.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import middleware.public.configurationCall as configCall
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask import session

def get_new_token(userid):

    """
        @Datetime ： 2024/9/30 00:02
        @Author ：eblis
        @Motto：简单描述用途
    """
    access_token = create_access_token(identity=userid)
    refresh_token = create_refresh_token(identity=userid)
    session['token'] = access_token
    session['user_id'] = userid
    datas = {
        'accessToken': access_token,
        'expires': int(configCall.expires_minutes) * 60 * 1000,  # 转换为毫秒
        'refreshToken': refresh_token,
        'tokenType': 'Bearer'
    }
    return datas


@jwt_required(refresh=True)
def get_refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return new_access_token

@jwt_required()
def get_verify_token():
    """
        @Datetime ： 2024/9/30 00:18
        @Author ：eblis
        @Motto：简单描述用途
    """
    user_id = get_jwt_identity()
    return user_id


@jwt_required()
def destroy_token():
    # 黑名单集合
    BLACKLIST = set()
    jti = get_jwt()['jti']  # 获取JWT的唯一标识符
    user_id = get_jwt_identity()  # 从JWT获取用户ID
    session.clear()  # 清除session
    BLACKLIST.add(jti)  # 将JWT添加到黑名单中

    return True
