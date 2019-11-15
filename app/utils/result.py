import json

from flask import jsonify, Response

from app.utils.code import ResponseCode


class Result:

    def __init__(self):
        self.code = ""
        self.msg = ""
        self.data = None
        self.tag = True

    @staticmethod
    def success(object):
        result = Result()
        result.code = ResponseCode.Success
        result.msg = "成功!"
        result.data = object
        return result

    @staticmethod
    def error(msg):
        result = Result()
        result.code = ResponseCode.Error
        result.msg = msg
        return result

    @staticmethod
    def warn(msg):
        result = Result()
        result.code = ResponseCode.Warn
        result.msg = msg
        return result

    @staticmethod
    def response(result):
        return Response(json.dumps({"code": result.code, "msg": result.msg, "data": result.data}),
                        mimetype='application/json')

    def response(self):
        return Response(json.dumps({"code": self.code, "msg": self.msg, "data": self.data}),
                        mimetype='application/json')

    @staticmethod
    def error_response():
        return jsonify({"code": -1, "msg": "应用错误"})

