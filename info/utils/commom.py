# 公用的自定义工具类
import functools

from flask import session, current_app, g


def to_index_class(index):
    """
    返回指定索引对应的类名
    自定义过滤器类
    """
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    return ""


"""
抽取公用用户信息查询类
"""
def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 获取当前登录用户的id
        user_id = session.get("user_id",None)
        user = None

        if user_id:
            # 尝试彩信用户模型
            from info.models import User
            user = User.query.get(user_id)

        g.user = user
        return f(*args, **kwargs)
    return wrapper
