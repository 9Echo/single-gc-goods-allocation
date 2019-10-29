# -*- coding: utf-8 -*-
# Description: 示例服务TodoList
# Created: shaoluyu 2019/06/19
# Modified: shaoluyu 2019/06/19; shaoluyu 2019/06/20

from flask import current_app
from flask import request
from flask_restful import Resource


class Hello(Resource):
    """TodoList资源
    """

    def get(self):
        try:
            # 获取get请求参数
            username = request.args.get('username', default='World')
            #
            data = {"message": "Hello, {}!".format(username)}
        except Exception as e:
            current_app.logger.exception(e)
            return {"code": -1, "msg": "系统错误"}, 500
        else:
            return {"code": 100, "msg": "成功", "data": data}, 200

    def post(self):
        """获取json列表参数
        """
        try:
            params = request.get_json(force=True)
            if not params:
                return {"code": 101, "msg": "输入数据错误"}, 400
            print("post params type: {}".format(type(params)))
            print("post params: {}".format(params))
        except Exception as e:
            current_app.logger.exception(e)
            return {"code": -1, "msg": "系统错误"}, 500
        else:
            return {"code": 100, "msg": "成功", "data": params}, 200
