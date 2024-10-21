# -*- coding: utf-8 -*-
"""
@Datetime ： 2024/2/24 15:16
@Author ： eblis
@File ：responseGO.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os
import sys

base_dr = str(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
bae_idr = base_dr.replace('\\', '/')
sys.path.append(bae_idr)

import json


class ResMsg:
    def __init__(self, code='00000', msg='Success', data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def to_dict(self):
        if self.data is None:
            return {
                'code': self.code,
                'msg': self.msg,
            }
        else:
            return {
                'code': self.code,
                'msg': self.msg,
                'data': self.data,
            }

    def to_json(self):
        return json.dumps(self.to_dict())

