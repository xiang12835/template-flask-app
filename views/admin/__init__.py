from . import index, other, user, video
from flask import Blueprint, request, url_for, session, abort


def create_bp_admin():
    admin_blu = Blueprint('admin', __name__, url_prefix='/admin')
    user.api.register(admin_blu, url_prefix='/user')
    index.api.register(admin_blu, url_prefix='/')
    video.api.register(admin_blu, url_prefix='/video')
    other.api.register(admin_blu, url_prefix='/other')
    return admin_blu

admin_blu = create_bp_admin()

# @admin_blu.before_request
# def before_request():
#     # 判断如果不是登录页面的请求
#     if not request.url.endswith(url_for("admin.login")):
#         user_id = session.get("user_id")
#         is_admin = session.get("is_admin", False)
#
#         if not user_id or not is_admin:
#             # 判断当前是否有用户登录，或者是否是管理员，如果不是，直接重定向到项目主页
#             abort(404)
