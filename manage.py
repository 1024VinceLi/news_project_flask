from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect  # 导入csrf防御模块
from flask_session import Session
app = Flask(__name__)
from flask_script import Manager  # 导入命令启动模块
from flask_migrate import  Migrate,MigrateCommand





manager = Manager(app)  # 创建Manager的实例对象






class Config(object):
    """配置信息类"""
    DEBUG = True

    # 配置mysql信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news_infor"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 集成redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session配置信息
    SESSION_TYPE = "redis"  # 指定session存储到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)  # 使用redis的实例
    PERMANENT_SESSION_LIFETIME = 86400  # 有效期(单位为秒)
    # 配置的是session的存储位置
    """
    flask 默认是将 session,进行加密,存储到了 cookie 中. 而 Django 默认是将 session 进行加密存
    储到了数据库中
    但是都没有存储到 Redis 中方便快速. 所以我们项目中将 session 存储到 redis 中
    
    """
    SECRET_KEY = "J12B234B23JAS14r34BJK"  # 设置session在cookie中的id加密的秘钥




# 从类中导入配置信息
app.config.from_object(Config)

# 获取mysql操作游标db
db = SQLAlchemy(app)

#创建StrictRedis对象，与redis服务器建⽴连接
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
"""
StrictRedis对象⽅法
指定参数host、port与指定的服务器和端⼝连接，
host默认为localhost，port默认为6379，db默认为0

使用该对象可以对数据库进行一下相应的操作

⽅法set，添加键、值，如果键不存在,就添加该键值,如果存在就把该键的值修改
如果添加成功则返回True，如果添加失败则返回False
result=sr.set('name','itheima')

  使用get可以获取键name的值
    result = sr.get('name')
    输出键的值，如果键不存在则返回None
                
    keys 输出响应结果，返回一个列表
        result=sr.keys()
"""


# 添加csrf配置信息
CSRFProtect(app)
"""
wtf 中的 csrf 验证就是由 csrfProtect 提供的.
所以只需要实例化 CSRFProtect 就可以开启 csrf验证.
补充: CSRFProtect 会对:
post,put,patch,delete. 这些操作进行校验
都是对服务器的数据有修改操作的. 而不是获取数据操
作.csrfProtect 只会对修改操作做校验.
"""


# 配置Session
Session(app)
"""
Session类中的init方法接收一个参数,就是app:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
如果没有app就自己初始化一个,所以这里我们给他传一个app         
"""

Migrate(app, db)  # 数据库迁移
"""
Migrate函数接收4个参数,其中有app和db都默认为None,但是后面会判断如果app和db为none的时候
会调用里面的init方法初始化app和db,所有传入app和db
"""
manager.add_command('db', MigrateCommand)  # 将数据库迁移命令注册到命令行启动命令中


@app.route('/')
def index():
    return "index"


if __name__ == '__main__':
    manager.run()