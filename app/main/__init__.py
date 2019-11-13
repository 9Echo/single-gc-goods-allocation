# -*- coding: utf-8 -*-
# Description: 用户模块
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29; shaoluyu 2019/06/20

from flask import Blueprint
from flask import jsonify
from flask_restful import Api

from app.main.routes.confirm_route import ConfirmRoute
from app.main.routes.hello import Hello
from app.main.routes.order_route import OrderRoute
from app.main.services.dispatch_service import get_stock

blueprint = Blueprint('main', __name__)
api = Api(blueprint)

# Routes
api.add_resource(Hello, '/hello')
api.add_resource(OrderRoute, '/order')
api.add_resource(ConfirmRoute, '/confirm')

@blueprint.route('/demo', methods=['GET'])
def demo():
    return jsonify({"name": "gc goods allocation"})




