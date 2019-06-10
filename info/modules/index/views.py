from flask import render_template, current_app, session
from info.modules.index import index_blu
from info.models import User, News


@index_blu.route('/')
def index():
    """
    显示首页
    1 如果用户已经登录,当前登录用户的数据传到模板中
    :return: 
    """
    # 取到用户id
    user_id = session.get("user_id")
    print("user_id: %s" % user_id)
    user = None
    if user_id:
        # 尝试查询用户模型
        try:

            user = User.query.get(user_id)
        except Exception as e:
           current_app.logger.error(e)

    # print("user: %s" % user)

    # print("data: %s" % data)


    # 右侧新闻排列展示
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(9)
    except Exception as e:
        current_app.logger.error(e)

    # 定义一个空的字典列表,里面装的就是字典
    news_dict_li = [news.to_basic_dict() for news in news_list]
    # 遍历对象列表,将对象的字典添加到字典列表中
    # for news in news_list:
    #     news_dict_li.append(news.to_basic_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li

    }

    return render_template("index.html",data=data)



# 在打开网页的时候,浏览器会自动向根路径请求图标
# send_static_file 是flask查找静态文件调用的方法
@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
# send_static_file: 发送静态文件. 找到项目的静态文件夹中的某个静态文件,并且返回