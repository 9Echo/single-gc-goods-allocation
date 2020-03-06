# -*- coding: utf-8 -*-
# Description: 切面
# Created: shaoluyu 2019/03/05
from flask import request


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
            cls.flask_app.logger.info('body is ' + str(request.json))
            cls.flask_app.logger.info('ip is ' + request.remote_addr)
