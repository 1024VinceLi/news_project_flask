from info import constants
from info.models import User, News
from info.modules.news import news_blu
from flask import render_template, session, current_app, abort,g

from info.utils.commom import user_login_data


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :return:
    """




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

    # 定义一个空字典,里面装的就是字典
    news_dict_li = [news.to_basic_dict() for news in news_list]
    news.clicks += 1 # 点击量加1

    data = {
        "user": g.user.to_dict() if g.user else None,
        "news_dict_li": news_dict_li,
        "news":news.to_dict()

    }

    return  render_template("detail.html",data=data)