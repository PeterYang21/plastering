from flask import Flask

def create_app():
    app = Flask(__name__)
    register_blueprints(app)
    return app

def register_blueprints(app):
    from api import api_blueprint
    app.register_blueprint(api_blueprint)