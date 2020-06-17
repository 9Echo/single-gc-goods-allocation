from flask_restful import Resource


class TestJmeter2(Resource):

    @staticmethod
    def get(name):
        print(name)
