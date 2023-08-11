from flask import Blueprint

video_blu = Blueprint('video', __name__, url_prefix='/video')

from . import video_api
