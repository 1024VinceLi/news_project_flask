from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect # 导入csrf防御模块

app = Flask(__name__)


class Config(object):
    """配置信息类"""
    DEBUG = True

    # 配置mysql信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news_infor"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 集成redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379









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





@app.route('/')
def index():
    return "index"


if __name__ == '__main__':
    app.run(debug=True)