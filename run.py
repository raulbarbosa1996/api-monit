from flask import Flask
from flask_cors import CORS

def create_server(filename):
    app = Flask(__name__)
    CORS(app)
    app.config.update(
        DEBUG = True,
        COUCHDB_SERVER = 'http://admin:admin@127.0.0.1:5984/',
        COUCHDB_DATABASE = 'intents'
    )

    app.config.from_object(filename)

    from Model_MySQL import db
    db.init_app(app)

    from app import api_bp
    app.register_blueprint(api_bp, url_prefix='/sr')

    from models import manager
    manager.setup(app)
    #manager.sync(app)

    return app


if __name__ == "__main__":
    app = create_server("config")
    app.run(port=6500)
