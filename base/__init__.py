import logging
import os
from dotenv import load_dotenv
from flask import Flask, current_app, request, redirect
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from libs.logger import setup_log
from config.config import config_dict
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class


db = SQLAlchemy()
redis_store = None

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)

# Initialize Flask-Uploads
photos = UploadSet('photos', IMAGES)


def create_app(config_name):
    app = Flask(__name__)

    config = config_dict.get(config_name)
    app.config.from_object(config)

    setup_log(log_file='logs/flask.log', level=config.LEVEL_LOG)

    Session(app)

    db.init_app(app)

    
    configure_uploads(app, photos)
    patch_request_class(app)
    
    # log
    # gunicorn_logger = logging.getLogger('gunicorn.error')
    # app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)
    # app.logger.info('nihao')

    @app.after_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Request-Method'] = "POST, PUT, GET, OPTIONS, DELETE"
        return response

    global redis_store
    # 创建redis的连接对象
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    from base.router import register_router
    register_router(app)

    return app
