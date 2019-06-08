from info.modules import index_blu
from info import redis_store

@index_blu.route('/')
def index():
    # session["name"] = "laowang"  # 做session测试
    # logging.debug("测试debug")
    # print(app)  # 测试current_app 代表当前项目的app


    redis_store.set("name", "laowang")
    # 向redis中保存一个键值

    return "index"