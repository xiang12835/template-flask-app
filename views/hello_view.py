from flask import Flask, jsonify    # 导入Flask模块
import pymysql
from flask import Blueprint, render_template, request, redirect, url_for


hello_bp = Blueprint('hello', __name__, url_prefix='/hello')


# app = Flask(__name__)      # 创建Flask实例，并指定模块名

def get_weather(city):
  # 根据城市名称查询天气
  # 返回查询结果
  return {'city': city, 'weather': 'sunny'}
  
@hello_bp.route('/weather/<city>')
def weather(city):
  # 调用get_weather函数获取天气情况
  result = get_weather(city)
  # 将查询结果以json格式返回
  return jsonify(result)

@hello_bp.route('/')   # 定义路由，即当访问 根目录 时返回下面的函数结果
def hello_world():
    return 'Hello, World!'   # 返回字符串Hello, World!

@hello_bp.route("/test_db")
def test_db():
    connection = pymysql.connect(
        host='127.0.0.1',  # 数据库IP地址
        port=3306,  # 端口
        user='root',  # 数据库用户名
        password='root',  # 数据库密码
        database='videodb'  # 数据库名称
    )
    return "恭喜，MySQL数据库已经连接上"


@hello_bp.route('/cipher')
def index():
    return render_template('practice_2_index.html')


@hello_bp.route('/cipher/<code>', methods=['GET'])
def check_(code):
    Cipher = '路由装饰器'
    if request.method == 'GET' and code == Cipher:
        return '使用GET方法，口令正确'


@hello_bp.route('/cipher/check', methods=['POST'])
def check():
    Cipher = '路由装饰器'
    cipher = request.form.get('cipher')
    if request.method == 'POST' and cipher == Cipher:
        return redirect(url_for('success'))


@hello_bp.route('/cipher/success')
def success():
    return '暗号对接成功！'



# if __name__ == '__main__':
#     app1.run()
