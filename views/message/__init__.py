from flask import Blueprint

msg_blu = Blueprint('message', __name__, url_prefix='/message')

from . import message_api
