from flask import render_template, current_app, session, request, jsonify

from info import constants
from info.modules.index import index_blu
from info.models import User, News
from info.utils.response_code import RET


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
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
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


@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    :return:
    """

    # 获取参数

    # 新闻分类的id
    cid = request.args.get("cid","1")

    # 获取页数,不传默认为获取第一页
    page = request.args.get("page",'1')

    # 每页多条数据
    per_page = request.args.get("per_page",'10')

    # 校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.PARAMERR, errmsg="参数")

    filters = []
    if cid != 1: # 查询的不是最新的数据
        # 需要添加套件
        filters.append(News.category_id == cid)

    # 3 查询数据
    try:
       paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 取到当前页面的数据
    news_model_list = paginate.items # 模型对象列表
    total_page = paginate.pages
    current_page = paginate.page


    # 将模型对象列表转成字典列表
    news_dict_li = []
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page":current_page,
        "news_dict_li":news_dict_li
    }
    return jsonify(errno = RET.OK, errmsg="OK" , data=data)











# 在打开网页的时候,浏览器会自动向根路径请求图标
# send_static_file 是flask查找静态文件调用的方法
@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
# send_static_file: 发送静态文件. 找到项目的静态文件夹中的某个静态文件,并且返回