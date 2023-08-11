

from flask import current_app
from flask_restful import Resource, reqparse, inputs

from models.user import UserLogin
from utils.auth_helper import Auth
from libs.http_lib import error, HttpCode


class LoginView(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('mobile', type=inputs.regex('1[3456789]\\d{9}'), required=True,
                            nullable=False, location=['form'], help='手机号参数不正确')
        parser.add_argument('password', type=str, required=True,
                            nullable=False, location=['form'], help='密码参数不正确')

        args = parser.parse_args()
        # 3.通过手机号取出用户对象
        try:
            user_login = UserLogin.query.filter(UserLogin.mobile == args.mobile).first()
        except Exception as e:
            current_app.logger.error(e)
            return error(code=HttpCode.db_error, msg='查询手机号异常')
        # 验证拿到的这个手机号  是否在我们的登陆信息中存在  异常捕获
        # 判断我们的用户信息不在返回错误的响应码
        if not user_login:
            return error(code=HttpCode.db_error, msg='用户不存在')
        return Auth().authenticate(args.mobile, args.password)

