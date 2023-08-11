from flask import jsonify

class HttpCode(object):
    ok = 200
    parmas_error = 400
    server_error = 500
    auth_error = 401
    db_error = 1001

def rep_result(code, msg, data):
    # {code=200, msg='ksdjksd', data={}}
    return jsonify(code=code, msg=msg, data=data or {})

def success(msg, data=None):
    return rep_result(code=HttpCode.ok, msg=msg, data=data)

def error(code, msg, data=None):
    return rep_result(code=code, msg=msg, data=data)
