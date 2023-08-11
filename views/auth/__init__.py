

from flask import Blueprint
from flask_restful import Api

from views.auth.login import LoginView

auth_blu = Blueprint('auth', __name__, url_prefix='/auth')

api = Api(auth_blu)

api.add_resource(LoginView, '/login')
