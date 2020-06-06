# -*- coding: utf-8 -*-
# Description: RestTemplate
# Created: shaoluyu 2020/06/06
import json
import requests
from requests import RequestException

from app.util.code import ResponseCode
from app.util.my_exception import MyException


class RestTemplate(object):
    @staticmethod
    def do_post(url, data):
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise RequestException
        if response.json().get('code') != 100:
            raise MyException('目标服务器错误', ResponseCode.Error)
        return response.json()
