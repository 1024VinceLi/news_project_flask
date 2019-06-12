from flask import g,redirect,render_template

from info.modules.profile import profile_blu
from info.utils.commom import user_login_data


@profile_blu.route('/info')
@user_login_data
def user_info():

    user = g.user

    # 查询用户是否存
    if not user:
        # 如果没有用户,代表没有登录,重定向到首页
        return redirect("/")

    data = {"user":user.to_dict()}
    return render_template("user.html",data=data)
