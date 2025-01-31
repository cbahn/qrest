
from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(None)
    # app.config.from_object('config.Config')
    app.config['DEBUG'] = True

    app.config['SECRET_KEY'] = Config.SECRET_KEY

    app.config['MONGO_URI'] = Config.MONGO_URI
    app.config['MONGO_CERT_PATH'] = Config.MONGO_CERT_PATH
    app.config['MONGO_DB_NAME'] = Config.MONGO_DB_NAME

    with app.app_context():

        from .registration.routes import registration_bp

        app.register_blueprint(registration_bp)

        return app