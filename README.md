## flask-app


### 系统架构

MVT: model -> view -> template (html)

MVJ: model -> view -> json


### 包安装

```
pip install flask==1.1.4
pip install Flask-Script
pip install flask-migrate==2.7.0
pip install Flask-Uploads
pip install Flask-Session==0.3.2
pip install Flask-SQLAlchemy==2.5.1
pip install Flask-Cors==3.0.10
pip install Flask-RESTful

pip install python-dotenv
pip install python-json-logger

pip install markupsafe==2.0.1 -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
pip install redis
pip install sqlalchemy==1.4.39 -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
pip install jwt
pip install faiss-cpu -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install tensorflow
pip install happybase
pip install py3Fdfs
pip install pymysql
pip install qiniu

pip install gunicorn
pip install jwt


pip install Werkzeug

ImportError: cannot import name 'secure_filename' from 'werkzeug'

#把 flask_upload.py 中的第26行拆分为两行
from werkzeug import secure_filename, FileStorage
#拆分结果
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

```





### 数据库迁移

```
flask shell # 进入一个交互式的 Python 编程
db.create_all() # 来创建所有的数据库表

python main.py shell
>>> from base import db
>>> db.create_all()
```


```
flask db init # 自动生成 migrations 文件夹
flask db migrate  # ⽣成迁移版本, 保存到迁移文件夹中
flask db upgrade  # 执行迁移

python main.py db init
python main.py db migrate
python main.py db upgrade
```


### 启动

python main.py runserver

http://127.0.0.1:5000/hello/

### Redis

报错：redis.exceptions.ReadOnlyError: You can't write against a read only replica.

解决：https://blog.csdn.net/huojiahui22/article/details/122448293




