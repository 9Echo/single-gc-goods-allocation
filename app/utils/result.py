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
