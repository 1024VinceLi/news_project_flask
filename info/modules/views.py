from info.modules import index_blu
from info import redis_store
from flask import render_template, current_app


@index_blu.route('/')
def index():
    # session["name"] = "laowang"  # 做session测试
    # logging.debug("测试debug")
    # print(app)  # 测试current_app 代表当前项目的app


    redis_store.set("name", "laowang")
    # 向redis中保存一个键值

    return render_template("index.html")



# 在打开网页的时候,浏览器会自动向根路径请求图标
# send_static_file 是flask查找静态文件调用的方法
@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
# send_static_file: 发送静态文件. 找到项目的静态文件夹中的某个静态文件,并且返回