import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session
import json
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from werkzeug.security import generate_password_hash


@passport_blu.route("/logout")
def logout():
    """
    退出功能：直接删除session
    :return:
    """
    session.pop("user_id", None)

    return jsonify(errno=RET.OK, errmsg="退出成功")


@passport_blu.route("/login", methods=["POST"])
def login():
    """
    1、接收参数
    2、校验参数  手机号格式  密码是否正确
    3、保持用户登录状态
    5、设置用户登录时间last_login
    4、返回响应

    :return:
    """
    dict_data= request.json
    mobile = dict_data.get("mobile")
    passport = dict_data.get("passport")

    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3、mobile  正则
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号的格式不正确")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户没有注册")

    if not user.check_passowrd(passport):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route("/register", methods=["POST"])
def register():
    """
    1、接收参数 mobile smscode password
    2、整体校验参数的完整性
    3、手机号格式是否正确
    4、从redis中通过手机号取出真是的短信验证码
    5、和用户输入的验证码进行校验
    6、初始化User()添加数据
    7、session保持用户登录状态
    8、返回响应
    :return:
    """
    # 1、接收参数 mobile smscode password
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    # 2、整体校验参数的完整性
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3、mobile  正则
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号的格式不正确")

    # 4、从redis中通过手机号取出真是的短信验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已经过期")

    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 核心逻辑 5、初始化User()添加数据
    user = User()
    user.nick_name = mobile
    # user.password_hash = generate_password_hash(password)
    user.password = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 7、session保持用户登录状态
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功")


# 1、请求的url是什么？
# 2、请求的方式是什么？
# 3、参数的名字是什么
# 4、返回给前端的参数和参数类型是什么
@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():

    """
    1、接收参数 mobile， image_code， image_code_id
    2、校验参数：mobile  正则
    3、校验用户输入的验证码和通过image_code_id查询出来的验证码是否一致
    4、先去定义一个随机的6验证码
    5、调用云通讯发送手机验证码
    6、将验证码保存到reids
    7、给前端一个响应
    :return:
    """
    # 因为json类型实际是一个字符串类型无法用到.get("mobile")
    # 需要将json类型转化为字典对象
    # json_data = request.data
    # dict_data = json.loads(json_data)
    # 如何去接受一个前端传入的json类型的数据
    dict_data = request.json

    # 1、接收参数 mobile， image_code， image_code_id
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2、全局的做一个检验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3、mobile  正则
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号的格式不正确")

    # 4、取出真实的验证码
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    # 核心逻辑 5、先去定义一个随机的6验证码,
    # "%06d" 将一个数字转化为6位数字，如果位数不够，用0填充   1234   001234
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.info("短信验证码为%s" % sms_code_str)

    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    #
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")

    # 6、将验证码保存到reids
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败")

    # 7、给前端一个响应
    return jsonify(errno=RET.OK, errmsg="成功发送短信验证码")


@passport_blu.route("/image_code")
def get_image_code():
    """
    /passport/image_code?imageCodeId=c1a16ab9-31d7-4a04-87c2-57c01c303828
    1、接收参数（随机的字符串）
    2、校验参数是否存在
    3、生成验证码  captche
    4、把随机的字符串和生成的文本验证码以key，value的形式保存到redis
    5、把图片验证码返回给浏览器
    :return:
    """
    # 1、接收参数（随机的字符串）
    image_code_id = request.args.get("imageCodeId")

    # 2、校验参数是否存在
    if not image_code_id:
        abort(404)

    # 3、生成验证码  captche
    _, text, image = captcha.generate_captcha()
    current_app.logger.info("图片验证码为%s" % text)

    # 4、把随机的字符串和生成的文本验证码以key，value的形式保存到redis
    try:
        redis_store.setex("ImageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
