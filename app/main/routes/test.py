from flask_restful import Resource


class TestJmeter(Resource):

    @staticmethod
    def post():

        print("test")
        return {"A": 1}