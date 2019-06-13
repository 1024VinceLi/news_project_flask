"""
一、集成配置类
二、集成sqlalchemy到flask
三、集成redis
四、集成csrfprotect
五、集成flask-session
六、集成flask-script
七、集成flask-migrate
"""
import logging

from flask import current_app
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app, db
from info.models import *

# 通过传入不同配置创造出不同配置下的app实例， 工厂方法  python设计模式：工厂模式
app = create_app("develop")


# 六、集成flask-script
manager = Manager(app)

# 七、集成flask-migrate, 在flask中对数据库进行迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    # print(app.url_map)
    manager.run()