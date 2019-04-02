from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from api import *
from mongoengine import *

if __name__ == "__main__":
    app = Flask('api')
    _api = Api(app)
    _api.add_resource(Login, '/login')
    _api.add_resource(BuildPlayground, '/build')
    app.run(debug=True)
