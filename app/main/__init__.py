# -*- coding: utf-8 -*-
# Description: 用户模块
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29; shaoluyu 2019/06/20

from flask import Blueprint
from flask import jsonify
from flask_restful import Api
from pymysql import MySQLError

from app.main.routes.confirm_route import ConfirmRoute
from app.main.routes.order_left_item_route import OrderLeftItemRoute
from app.main.routes.order_route import OrderRoute
from app.main.services.dispatch_service import get_stock
from app.utils.result import Result

blueprint = Blueprint('main', __name__)
api = Api(blueprint)

# Routes
# 订单请求
api.add_resource(OrderRoute, '/order')
# 推荐发货通知单确认反馈
api.add_resource(ConfirmRoute, '/confirm')
# 拼货请求
api.add_resource(OrderLeftItemRoute, '/orderleft')


@blueprint.route('/demo', methods=['GET'])
def demo():
    return jsonify({"name": "gc goods allocation"})


@blueprint.app_errorhandler(MySQLError)
def handle_mysql_exception(e):
    """封装数据库错误信息"""
    error = Result.error("数据库错误")
    return Result.response(error)


