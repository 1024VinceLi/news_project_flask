from flask import render_template, current_app, session

from info import redis_store
from info.models import User
from info.modules.index import index_blu


@index_blu.route('/')
def index():
    """
    显示首页
    1 如果用户已经登录,当前登录用户的数据传到模板中
    :return: 
    """
    # 取到用户id
    user_id = session.get("user_id",None)
    user = None
    if user_id:

       try:
           user = User.query.get(user_id)
       except Exception as e:
           current_app.logger.error(e)


    data = {
       "user": user.to_dict() if user else None
    }


    return render_template("index.html",data=data)



# 在打开网页的时候,浏览器会自动向根路径请求图标
# send_static_file 是flask查找静态文件调用的方法
@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
# send_static_file: 发送静态文件. 找到项目的静态文件夹中的某个静态文件,并且返回