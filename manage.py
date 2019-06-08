import logging
from flask import session
from info import create_app, db,models
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = create_app("develop")

Migrate(app, db)  # 数据库迁移
"""
Migrate函数接收4个参数,其中有app和db都默认为None,但是后面会判断如果app和db为none的时候
会调用里面的init方法初始化app和db,所有传入app和db
"""
manager = Manager(app)  # 创建Manager的实例对象

manager.add_command('db', MigrateCommand)  # 将数据库迁移命令注册到命令行启动命令中






if __name__ == '__main__':
    manager.run()