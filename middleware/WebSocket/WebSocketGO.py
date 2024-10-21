# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/9/26 23:45
@Author ： eblis
@File ：sys_menu_manage.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys


base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)



class WebSocketHandler():

    pass