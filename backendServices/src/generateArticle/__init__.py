# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/11/18 21:19
@Author ： eblis
@File ：__init__.py.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)
