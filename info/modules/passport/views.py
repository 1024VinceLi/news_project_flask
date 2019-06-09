from flask import request, abort, current_app, make_response, jsonify
import re
from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
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
    print(image_code_id)
    # 2 判断参数是否有值
    if not image_code_id:
        return abort(404)  # 如果没有值就返回404

    # 3 生成图片验证码
    name, text, image = captcha.generate_captcha()
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
    return jsonify(errno=RET.OK,errmsg="发送成功")


    # 1 获取参数: 手机号 图片验证码, 图片验证码编号
    params_dict = request.json  # 将传来的字符串字典类型转成json类型

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

    # 3 先从redis中取出真实的验证码内容
    try:
        # 所有的数据库操作都要用try包起来
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
        # 变量real_image_code为redis中真实的图片验证码
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片验证码查询失败")

    if not real_image_code:
        # 如果正常取出值,不存在,则验证码已经过期了
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 4 与用户的验证码内容进行对比,如果不一致,那么返回验证码输入错误
    if real_image_code.upper() != image_code_id.upper():
        """
        将验证码全都转为大写再比较
        无论用户输入的大写还是小写,都可以通过验证
        """
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5 如果一致着生成短信验证码
    # 随机数字,保证数字长度为6位,不够再前面补上0
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码的内容是: %s" % sms_code_str)

    # 6 发送短信验证码
    #  参数为 手机号   [短信内容, 过期时间] 短信模板编号
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES], 1)
    # 成功会默认返回0
    if result != 0:
        # result 不等于0 代表发送不成功
        return jsonify(errno=RET.THRDERR, errmsg="发送失败")

    # 将验证码保存在redis中(执行到这一步表示已经发送成功了)
    try:
        redis_store.set("SMS_" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7 告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")
