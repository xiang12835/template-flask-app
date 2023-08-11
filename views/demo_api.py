from models.user import UserInfo
from datetime import datetime
from flask import Blueprint


demo_bp = Blueprint('demo', __name__, url_prefix='/demo')


@demo_bp.route('/user_add')
def add_data():
    u = UserInfo()
    new_user1 = UserInfo(nickname='flask_test1', mobile='13323456789', signature='理想', create_time=datetime.now(),
                        role_id=1)
    new_user2 = UserInfo(nickname='flask_test2', mobile='13312345678', signature='梦想', create_time=datetime.now(),
                        role_id=2)
    u.add(new_user1)
    u.add(new_user2)
    return


@demo_bp.route('/user_delete')
def delete_data():
    delete_user = UserInfo.query.get(3)
    delete_user.delete()


@demo_bp.route('/user_update')
def update_data():
    u = UserInfo()
    update_user = u.query.get(3)
    update_user.status = 1
    u.update()


@demo_bp.route('/user_query1')
def query_data1():
    user_list = UserInfo.query.all()
    result = []
    for user in user_list:
        result.append(user.to_dict())
    return {'users': result}


@demo_bp.route('/user_query2')
def query_data2():
    user = UserInfo.query.get(3)
    return {'users': user.to_dict()}


@demo_bp.route('/user_query3')
def query_data3():
    first_user = UserInfo.query.first()
    return {'users': first_user.to_dict()}


@demo_bp.route('/user_query4')
def query_data4():
    user_list = UserInfo.query.filter(UserInfo.signature == '理想').all()
    result = []
    for user in user_list:
        result.append(user.to_dict())
    return {'users': result}


@demo_bp.route('/user_query5')
def query_data5():
    user_list = UserInfo.query.filter_by(signature='理想').all()
    result = []
    for user in user_list:
        result.append(user.to_dict())
    return {'users': result}

