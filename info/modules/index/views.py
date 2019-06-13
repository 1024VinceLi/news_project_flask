from flask import render_template, redirect, current_app, send_file, session, request, jsonify, g

from info import constants
from info.models import User, News, Category
from info.modules.index import index_blu
from info.utils.common import user_login
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    1、接收参数 cid page per_page
    2、校验参数合法性
    3、查询出的新闻（要关系分类）（创建时间的排序）
    4、返回响应，返回新闻数据
    :return:
    """
    # 1、接收参数 cid page per_page
    cid = request.args.get("cid")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    # 2、校验参数合法性
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3、查询出的新闻（要关系分类）（创建时间的排序）
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)
    # 怎么把空列表变成空呢？？？ [News.category_id == cid, News.create_time == "asdfasf"]
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()). \
            paginate(page, per_page, False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    news_list = paginate.items  # [obj, obj, obj]
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@index_blu.route("/")
@user_login
def index():
    # 需求：首页右上角实现，
    # 当我们进入到首页。我们需要判断用户是否登录，如果登录，将用户信息查出来，渲染给index.html
    user = g.user
    # 1、显示新闻排行列表
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()  # [obj, obj, obj]
    except Exception as e:
        current_app.logger.error(e)

    # [obj, obj, obj] --> [{}, {}, {}, {}]
    clicks_news_li = []

    for news_obj in clicks_news:
        clicks_news_dict = news_obj.to_basic_dict()
        clicks_news_li.append(clicks_news_dict)

    # 2、显示新闻分类
    categorys = []
    try:
        categorys = Category.query.all()  # [obj, obj]
    except Exception as e:
        current_app.logger.error(e)

    # categorys_li = []  # [{}, {}, {}]
    # for category in categorys:
    #     categorys_dict = category.to_dict()
    #     categorys_li.append(categorys_dict)
    # 使用列表表达式返回[{}, {}, {}]数据
    categorys_li = [category.to_dict() for category in categorys]

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li,
        "categorys": categorys_li
    }
    # data.user_info.avatar_url

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # redirect("/static/news/favicon.ico")
    # 返回图片
    return current_app.send_static_file("news/favicon.ico")
    # return send_file("/static/news/favicon.ico")