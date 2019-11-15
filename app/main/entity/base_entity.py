# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:32
# @Author  : Zihao.Liu
import datetime


class BaseEntity:
    """实体类的基类"""

    def as_dict(self):
        return {attr: self.get_attr(attr) for attr in self.__dict__.keys()}

    def get_attr(self, attr):
        value = getattr(self, attr)
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return value
