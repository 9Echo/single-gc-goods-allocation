# -*- coding: utf-8 -*-
# Description: 切面
# Created: shaoluyu 2019/03/05
from flask import request
from datetime import datetime
from app.main import blueprint
from flask import current_app


@blueprint.before_request
def before_request():
    current_app.logger.info('before_request')
    current_app.logger.info('method is ' + request.method)
    current_app.logger.info('url is ' + request.url)
    current_app.logger.info('body is ' + str(request.json).replace('\'', '"'))
    current_app.logger.info('ip is ' + request.remote_addr)


@blueprint.after_request
def after_request(response):
    current_app.logger.info("after_request")
    current_app.logger.info("body is " + str(response.json).replace("\'", '"'))
    current_app.logger.info("time is " + str(datetime.now())[:19])
    return response
