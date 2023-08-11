
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from base import db, create_app


app = create_app('dev')
CORS(app, supports_credentials=True)

# 管理器对象可以用来提供各种管理命令，例如启动应用程序、创建数据库表、导入数据等等
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
