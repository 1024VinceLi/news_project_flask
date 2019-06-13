import functools

from flask import current_app, session, g


def do_index_class(index):
    if index == 1:
        return "first"

    elif index == 2:
        return "second"

    elif index == 3:
        return "third"

    else:
        return ""


# def user_login():
#     user_id = session.get("user_id")
#     user = None
#
#     if user_id:
#         try:
#             from info.models import User
#             user = User.query.get(user_id)
#         except Exception as e:
#             current_app.logger.error(e)
#
#     return user


def user_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return func(*args, **kwargs)

    return wrapper