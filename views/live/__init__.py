

from . import rtmp, channel
from flask import Blueprint


def create_bp():
    live_blu = Blueprint('live', __name__, url_prefix='/live')
    rtmp.api.register(live_blu, url_prefix='/rtmp')
    channel.api.register(live_blu, url_prefix='/channel')
    return live_blu


live_blu = create_bp()
