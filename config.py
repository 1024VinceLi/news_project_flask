import logging
import redis


class Config(object):
    """配置信息类"""
    DEBUG = True  # 开启debug

    # 配置mysql信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news_infor"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 集成redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session配置信息
    SESSION_TYPE = "redis"  # 指定session存储到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis的实例
    PERMANENT_SESSION_LIFETIME = 86400  # 有效期(单位为秒)
    # 配置的是session的存储位置
    """
    flask 默认是将 session,进行加密,存储到了 cookie 中. 而 Django 默认是将 session 进行加密存
    储到了数据库中
    但是都没有存储到 Redis 中方便快速. 所以我们项目中将 session 存储到 redis 中

    """
    SECRET_KEY = "J12B234B23JAS14r34BJK"  # 设置session在cookie中的id加密的秘钥

    # 设置日志登记
    LOG_EVEL = logging.DEBUG



class DevelopConfig(Config):
    """开发环境下的配置"""
    DEBUG = True

class ProductConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_EVEL = logging.WARNING  # 配置生产环境日志等级


class TestingConfig(Config):
    """单元测试配置"""
    DEBUG = True
    TESTING = True


config = {  # 以字典的形式对函授进行封装,方便使用
    "develop":DevelopConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}
