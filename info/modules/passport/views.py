from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session
import re
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu
import random


@passport_blu.route("/image_code")
def get_image_code():
    """
    生成图片验证码并返回
    1 取到参数
    2 判断参数是否有值
    3 生成图片验证码
    4 保存图片验证码
    5 返回图片验证码
    :return: 
    """
    # 1 取到参数
    # args: 取到url中 ? 后面的参数
    # 这个获取到的imageCodeId是前端js生成的图片验证码的编号
    image_code_id = request.args.get("imageCodeId")  # 取参数,如果不存在就为None
    # 2 判断参数是否有值
    if not image_code_id:
        return abort(404)  # 如果没有值就返回404

    # 3 生成图片验证码
    name, text, image = captcha.generate_captcha()
    print("图片验证码: %s" % text)

    """
    captcha源码中的generate_captcha函数返回值有三个,
    1 name
    2 text 图片验证码的文字  
    3 验证码图片   
    """

    # 4 保存图片严重呢干嘛的文字内容到redis中
    # 所有对数据库的操作包括查询都要用try包裹起来
    try:  # 将接收到的前端传来的图片验证码编号作为键    验证码文字作为值      过期时间  存入redis中
        redis_store.set("ImageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)  # 如果没有保存成功就返回500

    # 5 返回验证码图片
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response


@passport_blu.route("/sms_code", methods=["POST"])
def send_sms_code():
    """
    发送短信验证码
    1 获取参数: 手机号,  图片验证码,  图片验证码编号(随机值)
    2 校验参数
    3 从redis中取出真实的验证码内容
    4 与用户的验证码内容进行对比
    5 如果一直,生成短信验证码内容
    6 发送短信验证码
    7 告知发送结果

    """
    # 测试
    # return jsonify(errno=RET.OK,errmsg="发送成功")


    # 1 获取参数: 手机号 图片验证码, 图片验证码编号
    params_dict = request.json  # 将传来的字符串字典类型转成json类型

    print(params_dict)

    # 提取手机号
    mobile = params_dict.get("mobile")

    # 提取图片验证码内容
    image_code = params_dict.get("image_code")

    # 提取图片验证码编号
    image_code_id = params_dict.get("image_code_id")

    # 2 校验参数
    # 判断是否有值
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 校验手机号是否正确
    if not re.match(r"1[345678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3 先从redis中取出真实的验证码内容,此步骤为了检验验证码是否过期
    try:
        # 所有的数据库操作都要用try包起来
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)  # 从数据库中取出来的是byte类型

        print("redis中的图片验证码id为: %s " % real_image_code)
        # 变量real_image_code为redis中真实的图片验证码
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片验证码查询失败")

    if not real_image_code:
        # 如果正常取出值,不存在,则验证码已经过期了
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 4 与用户的验证码内容进行对比,如果不一致,那么返回验证码输入错误
    print("图片验证码比较:  %s : %s" % (real_image_code.upper(), image_code.upper()))
    if real_image_code.upper() != image_code.upper():

        """
        将验证码全都转为大写再比较
        无论用户输入的大写还是小写,都可以通过验证
        """
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5 如果一致着生成短信验证码
    # 随机数字,保证数字长度为6位,不够再前面补上0
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码的内容是: %s" % sms_code_str)
    print("手机验证码: %s " % sms_code_str)

    # 6 发送短信验证码
    #  参数为 手机号   [短信内容, 过期时间] 短信模板编号
    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES], 1)
    # 成功会默认返回0

    # if result != 0:
    #     # result 不等于0 代表发送不成功
    #     return jsonify(errno=RET.THRDERR, errmsg="发送失败")

    # 将验证码保存在redis中(执行到这一步表示已经发送成功了)
    try:
        # 短信验证码在redis中的格式为SMS_开头
        redis_store.set("SMS_" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7 告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")



@passport_blu.route("/register",methods=['POST'])
def register():
    """
    注册逻辑
    1 获取参数
    2 校验参数
    3 取到服务器保存的真实短信内容荣
    4 校验用户输入的短信验证码内容和真实验证码内容是否是一致
    5 如果一致,初始化User模型,
     6 将 user模型添加到数据库
     7 返回响应
    :return: json errno错误码
    
    参数: mobile手机号  smscode短信验证码   password密码
    """
    # 1 获取参数
    param_dict = request.json

    # 提取手机号
    mobile = param_dict.get("mobile")

    # 提取短信验证码
    smscode = param_dict.get("smscode")

    # 提取密码
    password = param_dict.get("password")


    # 2 校验参数
    if not all([mobile, smscode, password]):
        return jsonify(erron=RET.PARAMERR, errmsg="参数不足")

    # 校验手机号是否正确
    if not re.match(r"1[345678]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3 取到服务器保存的真实短信验证码内容
    try:
        real_sms_code = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_sms_code:
        # 表示验证码已经过期了,取到了空
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    # 4 校验用户输入的短信验证码的内容和真实验证码的内容是否一致

    if int(real_sms_code) != int(smscode):
        print("注册时redis中的手机验证码比较:[ %s : %s] :[ %s : %s]" % (type(real_sms_code), real_sms_code, type(smscode), smscode))
        return jsonify(errno=RET.DATAERR, errmsg="手机验证码输入错误")

    # 5 如果一致,初始化User模型,并赋值
    user = User()
    user.mobile = mobile
    # 暂时没有昵称,用手机号代替
    user.nick_name = mobile
    # 记录最后一次登录的时间
    user.last_login = datetime.now()

    # TODO 对密码做处理
    # 设置password的时候对密码进行加密
    user.password = password
    # 6 添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg = "数据保存失败")

    # 往往session中保存数据表示当前已经登录
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 7 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/login', methods=["POST"])
def login():
    """
    登录
    1 获取参数
    2 校验参数
    3 校验密码
    4 保存用户状态
    5 响应
    :return: 
    """
    # 1 获取参数
    params_dict = request.json

    # 提取手机号
    mobile = params_dict.get("mobile")

    # 提取密码
    passport = params_dict.get("passport")

    # 2 校验参数
    if not all([mobile, passport]):
        return jsonify(erron=RET.PARAMERR, errmsg="参数不足")

    # 校验手机号是否正确
    if not re.match(r"1[345678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3 校验密码
    try:
       user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 校验登录的密码和当前用户的密码是否一致
    if not user.check_passowrd(passport):
        return jsonify(errno=RET.PWDERR, errmsg="用户名和密码错误")

    # 4 保存用户登录状态
    session["userr_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name


    # 设置当前洪湖最后一次登录时间
    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    # 5 响应
    return jsonify(errno=RET.OK, errmsg="登录成功")






