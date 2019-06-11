from info import constants
from info.models import User, News
from info.modules.news import news_blu
from flask import render_template, session, current_app, abort, g, jsonify, request

from info.utils.commom import user_login_data
from info.utils.response_code import RET


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :return:
    """
    # 假设该用户没有收藏
    is_collected =False
    user = g.user





    # news = None
    # 查询新闻数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not news:
        # 返回未找到页面
        print("new:没有")
        abort(404)

    # 右侧新闻排列逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:
        current_app.logger.error(e)



    if user:
        # 判断用户是否收藏了当前的新闻
        if news in user.collection_news:
            print("用户已经收藏了该新闻")
             # 在用户的收藏列表中查询是否存在,
             # 如果存在则表示已经收藏过了
            is_collected = True

    # 定义一个空字典,里面装的就是字典
    news_dict_li = [news.to_basic_dict() for news in news_list]
    news.clicks += 1 # 点击量加1

    data = {
        "user": g.user.to_dict() if g.user else None,
        "news_dict_li": news_dict_li,
        "news":news.to_dict(),
        "is_collected":is_collected

    }

    return  render_template("detail.html",data=data)



@news_blu.route("/news_collect",methods=["POST"])
@user_login_data
def collect_news():
    """
    新闻收藏
    1 接受参数
    2 判断参数
    3 查询新闻,并判断新闻是否存在
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1 接受参数
    news_id = request.json.get("news_id")
    print("news_id: %s" % news_id)
    action = request.json.get("action")
    print("action: %s" % action)
    # 2 判断参数是否都有
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3 判断参数是否是收藏和取消收藏
    if action not  in ["collect","cancel_collect"]:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    try:
        # 新闻id转数字类型
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=RET.PARAMERR, errmsg="参数不挣钱")

    # 查询新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.looger(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到任何数据")

    # 4 收藏以及取消收藏
    if action == "cancel_collect":
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)

    else:
        # 收藏
        if news not in user.collection_news:
            # 添加到用户的新闻收藏列表
            user.collection_news.append(news)

    return jsonify(errno=RET.OK, errmsg="收藏成功")











