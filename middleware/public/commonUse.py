# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/29 13:23
@Author ： eblis
@File ：commonUse.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import os
import sys
import time

import requests

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)


import random
import string
import datetime
import ast
import bcrypt
import jwt
import logging
from collections import defaultdict
from cachetools import TTLCache

import middleware.public.configurationCall as configCall

class verifyGO():

    def generate_token(self, user_id, secret_key, expires_in_minutes):
        # 创建载荷，包含用户ID和过期时间
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)
        }

        # 使用HS256算法和私钥对载荷进行签名，生成JWT
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return token


    def verify_token(self, token, secret_key):
        try:
            # decode方法会验证签名和检查有效期
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            # 如果JWT已经过期，decode方法会抛出这个异常
            print("Token is expired")
            return None
        except jwt.InvalidTokenError:
            # 如果JWT不合法（例如，签名不正确），decode方法会抛出这个异常
            print("Token is invalid")
            return None

class customCache():
    def __init__(self, maxsize=2, ttl=1800):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def write_to_cache(self, key, value):
        """
            @Datetime ： 2024/6/15 15:40
            @Author ：eblis
            @Motto：写入缓存
        """
        self.cache[key] = value

    def read_from_cache(self, key):
        """
            @Datetime ： 2024/6/15 15:40
            @Author ：eblis
            @Motto：读取指定key 的缓存
        """

        return self.cache.get(key)


class otherUse():
    def __init__(self):
        # 初始化基础日志记录器
        self.logger = logging.getLogger(__name__)
        self.app = None

    def init_app(self, app):
        """初始化与Flask应用的连接"""
        self.app = app

    def build_tree(self, menu_items):
        """
        构建菜单树
        :param menu_items: 数据库提取的菜单项列表
        :return: 菜单树
        """
        # 创建字典存储菜单项，以便快速访问
        menu_dict = {}
        # 初始化 children 默认值为空列表
        children_map = defaultdict(list)

        # 构造基本的菜单字典
        for item in menu_items:
            menu_dict[item['id']] = {
                'path': item['route_path'],
                'component': item['component'],
                'redirect': item.get('redirect', ''),
                'name': item.get('route_name', ''),
                'meta': {
                    'title': item['name'],
                    'icon': item.get('icon', ''),
                    'hidden': item.get('visible', 0) == 0,
                    'alwaysShow': item.get('always_show', 0) == 1,
                    'keepAlive': item.get('keep_alive', 0) == 1,
                },
                'children': []  # 初始化为空
            }
            # 收集子菜单
            children_map[item['parent_id']].append(item['id'])

        # 构建树形结构
        for parent_id, children_ids in children_map.items():
            if parent_id in menu_dict:  # 如果有对应的父节点
                menu_dict[parent_id]['children'] = [menu_dict[child_id] for child_id in children_ids]

        # 返回顶级菜单（没有父级的菜单）
        tree = [menu_dict[item_id] for item_id in children_map[0]]
        return tree

    def normalize_text(self, text):
        replacements = {
            '‘': "'", '’': "'",  # 替换为普通单引号
            '“': '"', '”': '"',  # 替换为普通双引号
            '—': '-',  # 替换为普通连字符
            '\xa0': ' ',  # 替换为普通空格
            '\u30fb': "'",

            # 添加其他需要替换的字符
        }
        # 先移除 GBK 不支持的字符
        cleaned_text = text.encode("gbk", errors="ignore").decode("gbk", errors="ignore")

        # 执行替换
        for old, new in replacements.items():
            cleaned_text = cleaned_text.replace(old, new)

        return cleaned_text

    def change_hashed(self, data):
        # 转换字符串为bytes类型，因为bcrypt只能处理bytes
        data = data.encode('utf-8')

        # 生成salt
        salt = configCall.fixed_salt.encode('utf-8')

        # 生成哈希密码
        hashed_data = bcrypt.hashpw(data, salt)

        return hashed_data.decode('utf-8')  # 将bytes类型转换为字符串



    def add_cors_headers(self, response):
        """用于添加 CORS 头部到响应中"""
        response.headers.add('Access-Control-Allow-Origin', 'https://ilcin.online')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    def get_new_proxy(self, wait):
        time.sleep(int(wait))
        try:
            response = requests.get(configCall.proxy_add)
            proxy = response.text.strip()

        except Exception as e:
            print(f"Error fetching new proxy: {e}")
            return None
        else:
            try:
                proxys = self.changeDict(proxy)
                if proxys["success"] == "false":
                    return None
                else:
                    # print(f"这次使用：{proxy}")
                    return {"http": proxy, "https": proxy}  # 返回代理字典
            except:
                # print(f"这次使用：{proxy}")
                return {"http": proxy, "https": proxy}  # 返回代理字典

    def changeDict(self, data):
        """
            @Datetime ： 2024/6/15 15:40
            @Author ：eblis
            @Motto：简单描述用途
        """
        if isinstance(data, dict):
            # self.sendlog("data 是一个字典类型")
            thisStep = data
        else:
            # self.sendlog("data 不是一个字典类型")
            try:
                thisStep = ast.literal_eval(data)
            except:
                try:
                    thisStep = json.loads(data)
                except:
                    thisStep = data

        return thisStep

    def changeIsinstance(self, data, type):
        """
            @Datetime ： 2024/6/15 15:40
            @Author ：eblis
            @Motto：简单描述用途
        """
        if isinstance(data, type):
            # self.sendlog(f"data 是一个{type}类型")
            thisStep = data
        else:
            # self.sendlog(f"data 不是一个{type}类型")
            thisStep = ast.literal_eval(data)
        return thisStep

    def sendlog(self, contents):
        """
        统一的日志记录方法，确保在应用上下文中运行
        """
        try:
            if self.app:
                # 使用应用上下文
                with self.app.app_context():
                    self.app.logger.info(contents)
            else:
                # 如果没有应用实例，使用基础日志记录器
                self.logger.info(contents)
        except Exception as e:
            # 确保至少能打印到控制台
            print(f"日志记录错误: {e}")
            print(contents)

    def make_folder(self, path, name=None):
        """
            @Datetime ： 2024/6/13 12:31
            @Author ：eblis
            @Motto：简单描述用途
        """
        if name is None:
            folder_path = f"{path}"
        else:
            folder_path = f"{path}/{name}"
        # 检查 logs 文件夹是否存在，如果不存在则创建
        # print("folder_path", folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.sendlog(f" {folder_path} 添加 successfully.")
        else:
            self.sendlog(f"{folder_path} 已经存在，不需要重复新建文件夹")
        return folder_path

    def make_file(self, path, name=None):
        """
            @Datetime ： 2024/6/13 12:31
            @Author ：eblis
            @Motto：简单描述用途
        """
        if name is None:
            file_path = f"{path}"
        else:
            file_path = f"{path}/{name}"
        # 检查文件是否存在，如果不存在则创建
        if not os.path.isfile(file_path):
            open(file_path, 'w').close()
            print(f"文件 {file_path} 已成功创建.")
        else:
            print(f"文件 {file_path} 已经存在，不需要重复创建.")
        return file_path


    def redome_sample(self, listdata, num):
        """
            @Datetime ： 2024/8/4 23:50
            @Author ：eblis
            @Motto：随机打乱列表的顺序
        """

        return random.sample(listdata, num)

    def redome_shuffle(self, sequence):
        """
            @Datetime ： 2024/8/4 23:50
            @Author ：eblis
            @Motto：随机打乱列表的顺序
        """
        random.shuffle(sequence)
        return sequence

    def redome_string(self, mo, masL, maxL):
        """
            @Datetime ： 2024/5/7 15:39
            @Author ：eblis
            @Motto：pwd:0 有特殊字符，1没特殊字符,2 小写字母,3 纯字母，不分大小写
        """
        if mo == "符号+数字+字母":
            characters = string.ascii_letters + string.digits + string.punctuation

        elif mo == "数字+字母":
            characters = string.ascii_letters + string.digits

        elif mo == "小写字母":  # 添加纯小写字母
            characters = string.ascii_lowercase
        else:
            print(f"{mo}")
            characters = string.ascii_letters

        length = self.randomRandint(int(masL), int(maxL))
        rdata = ''.join(random.choice(characters) for _ in range(length))

        return rdata

    def randomRandint(self, a, b):
        if a == '' or b == '':
            return False
        return random.randint(a, b)

    def randomChoice(self, sequence):
        """
            @Datetime ： 2024/5/7 15:39
            @Author ：eblis
            @Motto：列表，元组，字符串都属于sequence
        """
        return random.choice(sequence)

    def turn_isoformat(self, timedata):
        # print("timedata",type(timedata),timedata)
        if type(timedata) == datetime.datetime:
            new_timedata = timedata.strftime("%Y-%m-%d %H:%M:%S")
        else:
            new_timedata = timedata
        return new_timedata

    def split_evenly(self, lst, num):
        """
            @Datetime ： 2024/5/7 15:39
            @Author ：eblis
            @Motto：函数的主要目的是将一个列表均匀地分割成指定数量的小列表
        """

        avg_size = len(lst) // num
        split_lst = [lst[i:i + avg_size] for i in range(0, len(lst), avg_size)]
        remainder = len(lst) % num
        for i in range(remainder):
            split_lst[i].append(lst[avg_size * num + i])
        return split_lst
