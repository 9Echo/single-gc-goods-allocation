# -*- coding: utf-8 -*-
# Description: 用户模块
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29; shaoluyu 2019/06/20

from flask import Blueprint
from flask import jsonify
from flask_restful import Api
from app.main.routes import compose_route
from app.main.routes.compose_route import ComposeRoute
from app.main.routes.confirm_route import ConfirmRoute
from app.main.routes.goods_allocation_route import GoodsAllocationRoute
from app.main.routes.order_route import OrderRoute
from app.main.routes.loading_route import LoadingRoute
from app.main.routes.test import TestJmeter
from app.main.routes.test2 import TestJmeter2
from app.test.main.routes.order_route_test import OrderRouteTest

blueprint = Blueprint('main', __name__)
api = Api(blueprint)

# Routes
# 订单请求
api.add_resource(OrderRoute, '/order')
# 订单请求测试
api.add_resource(OrderRouteTest, '/orderTest')
# 推荐发货通知单确认反馈
api.add_resource(ConfirmRoute, '/confirm')
# 拼单推荐
api.add_resource(ComposeRoute, '/compose')
# 配载图请求
api.add_resource(LoadingRoute, '/loading')
# 钢厂智能分货请求
api.add_resource(GoodsAllocationRoute, '/goodsAllocation')
api.add_resource(TestJmeter, "/test")
api.add_resource(TestJmeter2, "/test2")


@blueprint.route('/demo', methods=['GET'])
def demo():
    return jsonify({"name": "gc goods allocation"})

