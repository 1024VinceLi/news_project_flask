#  创建一个存放业务逻辑包
from logging.handlers import RotatingFileHandler
import logging
from flask import Flask
from config import config  # 将config字典导入
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session


# config = {
#     "develop": DevelopConfig,
#     "product": ProductConfig,
#     "testing": TestingConfig
# }

# db = SQLAlchemy(app) 拆分成2步
# db = SQLAlchemy()
# db.init_app(app)
from info.utils.common import do_index_class

db = SQLAlchemy()


def set_log(config_name):
    # 通过不同的人配置创建出不同日志记录
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


redis_store = None  # type: StrictRedis


# 只要是可变的参数，一、可以放在配置文件中，二、用函数封装 三、用全局变量
# 可所有可变的参数用函数的形参来代替
def create_app(config_name):
    set_log(config_name)
    app = Flask(__name__)
    # 一、集成配置类
    app.config.from_object(config[config_name])

    # 二、集成sqlalchemy到flask
    db.init_app(app)

    # 三、集成redis  可以吧容易产生变化的值放入到配置中
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)
    # 四、CSRFProtect, 只起到保护的作用，具体往表单和cookie中设置csrf_token还需要我们自己去做

    # 1、先往cookie中添加一个csrf_token
    # 2、往表单中去设置， 现在我们有表单吗？如何在ajax中去设置一个csrf_token
    @app.after_request
    def after_request(response):
        # 通过wtf这个扩展给我们生成的token值
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)

        return response
    CSRFProtect(app)

    # 集成flask-session
    # 说明: flask中的session是保存用户数据的容器（上下文），而flask_session中的Session是指定session的保存路径
    Session(app)

    # 添加过滤器
    app.add_template_filter(do_index_class, "index_class")

    # 注册蓝图
    # 对于index_blu只导入一次，什么时候调用什么时候导入，解决循环导入问题的方法
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    return app