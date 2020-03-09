# -*- coding: utf-8 -*-
# Description: 切面
# Created: shaoluyu 2019/03/05
from flask import request, g
from app.main.routes.order_route import OrderRoute
from datetime import datetime


class Aspect(object):
    """切面类

        提供日志输出、请求校验等
        """
    flask_app = None

    @classmethod
    def init(cls, app):
        cls.flask_app = app
        Aspect.aspect_log()

    @classmethod
    def aspect_log(cls):
        @cls.flask_app.before_request
        def before_request():
            cls.flask_app.logger.info('before_request')
            cls.flask_app.logger.info('method is ' + request.method)
            cls.flask_app.logger.info('url is ' + request.url)
            cls.flask_app.logger.info('body is ' + str(request.json).replace('\'', '"'))
            cls.flask_app.logger.info('ip is ' + request.remote_addr)

        @cls.flask_app.after_request
        def after_request(response):
            cls.flask_app.logger.info("after_request")
            cls.flask_app.logger.info("body is " + str(response.json).replace("\'", '"'))
            cls.flask_app.logger.info("time is " + str(datetime.now())[:19])
            return response
