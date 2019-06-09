from flask import request, abort, current_app, make_response

from info import redis_store, constants
from info.utils.captcha.captcha import captcha
from . import passport_blu

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
        return abort(404) # 如果没有值就返回404

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
        redis_store.set("ImageCodeId_"+image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)  # 如果没有保存成功就返回500

    # 5 返回验证码图片
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response








