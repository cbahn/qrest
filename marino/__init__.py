from flask import Flask, render_template
from .config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
import os

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(None)

    # This tells flask recognize X-Forwarded-Proto headers
    # So it knows what url to use for redirects
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config['PREFERRED_URL_SCHEME'] = 'https'    

    app.config['SECRET_KEY'] = Config.SECRET_KEY

    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MONGO_DB_NAME'] = Config.MONGO_DB_NAME

    with app.app_context():

        from .registration import routes as registration_routes
        app.register_blueprint(registration_routes.registration_bp)

        from .location import routes as location_routes
        app.register_blueprint(location_routes.registration_bp)

        from .menu import routes as menu_routes
        app.register_blueprint(menu_routes.registration_bp)

        from .admin import routes as admin_routes
        app.register_blueprint(admin_routes.registration_bp)

        @app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.jinja2'), 404

        return app