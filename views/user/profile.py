
import hashlib
import os
from flask import g, request, current_app
from models.user import UserInfo
from views.user import user_blu
from libs.image_upload import image_storage
from utils.common import auth_identify, check_file_type
from utils.constants import QINIU_DOMIN_PREFIX
from libs.fastdfs.fdfs import FastDFSStorage
from libs.http_lib import error, HttpCode, success
from base.settings import BASE_DIR

from libs.logger import json_log
user_action_log = json_log('user_action', 'logs/user_action.log')

@user_blu.route('/user_upd', methods=['GET', 'POST'])
@auth_identify
def user():
    if request.method == 'GET':
        data = g.user.to_dict()
        return success(msg='获取用户信息成功', data=data)
    data_dict = request.form
    nickname = data_dict.get('nickname')
    # avatar_url = data_dict.get('avatar_url')
    signature = data_dict.get('signture')
    sex = data_dict.get('sex')
    birth_date = data_dict.get('birthday')

    cur_user = g.user
    cur_user.nickname = nickname
    # cur_user.avatar_url = avatar_url
    cur_user.signature = signature
    cur_user.sex = sex
    cur_user.birth_date = birth_date
    try:
        cur_user.update()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='修改资料失败')
    user_action_log.warning(
        {'user_id': cur_user.id, 'url': '/profile/user', 'method': 'post', 'msg': 'update user_info'})
    return success(msg='修改个人信息资料成功')


@user_blu.route('/pass_info')
@auth_identify
def pass_info():
    """
    密码修改接口
    :return: code msg
    """
    # 判断我们当前访问的这个用户是不是登陆的用户
    if not g.user:
        return error(HttpCode.auth_error, '用户未登陆')
    # 2.获取参数,老密码,新密码
    dict_data = request.json
    old_password = dict_data.get("old_password")
    new_password = dict_data.get("new_password")

    # 3.校验参数
    if not all([old_password, new_password]):
        return error(code=HttpCode.parmas_error, msg="参数不完整,新旧密码不能为空")

    # 4.判断老密码正确性
    if not g.user.check_passowrd(old_password):
        return error(code=HttpCode.parmas_error, msg="初始密码输入不正确")

    # 5.设置新密码
    g.user.password = new_password

    # 6.返回响应
    return success(msg="修改密码成功")


@user_blu.route('/pic_info', methods=['POST'])
@auth_identify
def pic_info():
    """
    上传图片   用户头像
    /profile/pic_info
    :return: code msg
    """
    # 获取参数
    file_avatar = request.files.get('avatar')
    # 校验参数 有没有的问题
    if not file_avatar:
        return error(code=HttpCode.parmas_error, msg="参数不完整, 没有文件")
    # 检查文件类型
    if not check_file_type(file_avatar.filename):
        return error(code=HttpCode.parmas_error, msg='上传图片格式有误，请重新上传')
    try:
        # 读取内容
        img_data = file_avatar.read()
        # 上传
        image_name = image_storage.image_storage(img_data)
    except Exception as e:
        current_app.logger.error(e)
        return error(HttpCode.db_error, '上传失败')
    user = g.user
    user.avatar_url = QINIU_DOMIN_PREFIX + image_name
    user.update()

    # 更新操作
    return success('上传成功', data={'avatar_url': QINIU_DOMIN_PREFIX + image_name})


@user_blu.route('/pic/<int:user_id>', methods=['POST'])
def pic(user_id):
    """
    上传图片   用户头像
    /profile//pic/<int:user_id>
    :return: code msg
    """
    # 获取参数
    file_avatar = request.files.get('file')
    # 校验参数 有没有的问题
    if not file_avatar:
        return error(code=HttpCode.parmas_error, msg="参数不完整, 没有文件")
    # 检查文件类型
    if not check_file_type(file_avatar.filename):
        return error(code=HttpCode.parmas_error, msg='上传图片格式有误，请重新上传')
    name = file_avatar.filename
    path = os.path.join(BASE_DIR, f'avatar/{name}')
    file_avatar.save(path)
    try:
        avatar_url = FastDFSStorage().url(path)
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.parmas_error, msg='fdfs上传失败')
    user = UserInfo.query.get(user_id)
    user.avatar_url = avatar_url
    user.update()
    user_action_log.warning({
        'user_id': user_id,
        'url': f'/profile/pic/{user_id}',
        'method': 'post',
        'msg': 'upload avatar',
        'event': 'profile',
    })
    # 更新操作
    return success('上传成功', data={'avatar_url': avatar_url})


@user_blu.route('/user_info')
@auth_identify
def user_info():
    # 判断用户是否登陆

    return success('信息获取成功', data=g.user.to_dict())


def get_hash(byte_info):
    md5_1 = hashlib.md5()
    md5_1.update(byte_info)
    ret = md5_1.hexdigest()
    return ret