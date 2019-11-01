# -*- coding: utf-8 -*-
# Description: 用户模块
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29; shaoluyu 2019/06/20

from flask import Blueprint
from flask import jsonify
from flask_restful import Api
from app.main.routes.hello import Hello

blueprint = Blueprint('main', __name__)
api = Api(blueprint)

# Routes
api.add_resource(Hello, '/hello')


@blueprint.route('/demo', methods=['GET'])
def demo():
    return jsonify({"name": "flask demo"})



