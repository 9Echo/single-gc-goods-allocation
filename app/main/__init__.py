# -*- coding: utf-8 -*-
# Description: 用户模块
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29; shaoluyu 2019/06/20

from flask import Blueprint
from flask import jsonify
from flask_restful import Api
from pymysql import MySQLError

from app.main.routes import compose_route
from app.main.routes.compose_route import ComposeRoute
from app.main.routes.confirm_route import ConfirmRoute
from app.main.routes.order_route import OrderRoute
from app.utils.result import Result

blueprint = Blueprint('main', __name__)
api = Api(blueprint)

# Routes
# 订单请求
api.add_resource(OrderRoute, '/order')
# 推荐发货通知单确认反馈
api.add_resource(ConfirmRoute, '/confirm')
# 拼单推荐
api.add_resource(ComposeRoute, '/compose')


@blueprint.route('/demo', methods=['GET'])
def demo():
    return jsonify({"name": "gc goods allocation"})


# @blueprint.route('/compose', methods=['GET'])
# def compose():
#     ds = compose_route.compose(1)
#     return 200


@blueprint.app_errorhandler(MySQLError)
def handle_mysql_exception(e):
    """封装数据库错误信息"""
    return Result.error_response("数据库错误")


@blueprint.app_errorhandler(KeyError)
def handle_key_exception(e):
    """封装数据库错误信息"""
    return Result.error_response("缺少输入参数")


@blueprint.app_errorhandler(ValueError)
def handle_value_exception(e):
    """封装数据库错误信息"""
    return Result.error_response("传入参数的值错误")


@blueprint.app_errorhandler(TypeError)
def handle_type_exception(e):
    """封装数据库错误信息"""
    return Result.error_response("传入参数的类型错误")


