$(function(){

	// 打开登录框
	$('.login_btn').click(function(){
        $('.login_form_con').show();
	})
	
	// 点击关闭按钮关闭登录框或者注册框
	$('.shutoff').click(function(){
		$(this).closest('form').hide();
	})

    // 隐藏错误
    $(".login_form #mobile").focus(function(){
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function(){
        $("#login-password-err").hide();
    });

    $(".register_form #mobile").focus(function(){
        $("#register-mobile-err").hide();
    });
    $(".register_form #imagecode").focus(function(){
        $("#register-image-code-err").hide();
    });
    $(".register_form #smscode").focus(function(){
        $("#register-sms-code-err").hide();
    });
    $(".register_form #password").focus(function(){
        $("#register-password-err").hide();
    });


	// 点击输入框，提示文字上移
	// $('.form_group').on('click focusin',function(){
	// 	$(this).children('.input_tip').animate({'top':-5,'font-size':12},'fast').siblings('input').focus().parent().addClass('hotline');
	// })

    // 拷贝过来的修改前端页面BUG的代码
    $('.form_group').on('click',function(){
        $(this).children('input').focus()
    })
    //

    $('.form_group input').on('focusin',function(){
        $(this).siblings('.input_tip').animate({'top':-5,'font-size':12},'fast')
        $(this).parent().addClass('hotline');
    })

	// 输入框失去焦点，如果输入框为空，则提示文字下移
	$('.form_group input').on('blur focusout',function(){
		$(this).parent().removeClass('hotline');
		var val = $(this).val();
		if(val=='')
		{
			$(this).siblings('.input_tip').animate({'top':22,'font-size':14},'fast');
		}
	})


	// 打开注册框
	$('.register_btn').click(function(){
		$('.register_form_con').show();
		generateImageCode()
	})


	// 登录框和注册框切换
	$('.to_register').click(function(){
		$('.login_form_con').hide();
		$('.register_form_con').show();
        generateImageCode()
	})

	// 登录框和注册框切换
	$('.to_login').click(function(){
		$('.login_form_con').show();
		$('.register_form_con').hide();
	})

	// 根据地址栏的hash值来显示用户中心对应的菜单
	var sHash = window.location.hash;
	if(sHash!=''){
		var sId = sHash.substring(1);
		var oNow = $('.'+sId);		
		var iNowIndex = oNow.index();
		$('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
		oNow.show().siblings().hide();
	}

	// 用户中心菜单切换
	var $li = $('.option_list li');
	var $frame = $('#main_frame');

	$li.click(function(){
		if($(this).index()==5){
			$('#main_frame').css({'height':900});
		}
		else{
			$('#main_frame').css({'height':660});
		}
		$(this).addClass('active').siblings().removeClass('active');
		$(this).find('a')[0].click()
	})

    // TODO 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val()
        var password = $(".login_form #password").val()

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 发起登录请求
        var params = {
        "mobile": mobile,
        "passport": password
    }

    $.ajax({
        url: "/passport/login",
        type: "post",
        contentType: "application/json",
        // 在header中添加csrf_token随机值
        headers:{
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 代表登录成功
                location.reload()
            } else {
                alert(resp.errmsg)
                $("#login-password-err").html(resp.errmsg)
                $("#login-password-err").show()
            }
        }

    })

    })


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作
        e.preventDefault()

		// 取到用户输入的内容
        var mobile = $("#register_mobile").val()
        var smscode = $("#smscode").val()
        var password = $("#register_password").val()

		if (!mobile) {
            $("#register-mobile-err").show();
            return;
        }
        if (!smscode) {
            $("#register-sms-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

		if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        // 发起注册请求
        var params = {
        // 三个参数 手机号 验证码  验证码编号
        "mobile":mobile,
        "smscode":smscode,
        "password": password
    }
     // 发起注册请求
    $.ajax({
        //请求地址
        url:"/passport/register",
        // 请求方式
        type:"post",
        // 请求参数 JSON 要大写
        data:JSON.stringify(params),
        //请求参数的数据类型
        contentType:"application/json",

        success:function (response) {
            if(response.errno == "0"){
                //代表注册成功
                location.reload()
                //注册成功就刷新界面
            }else{
                //代表注册失败
                alert(response.errmsg)
                
                $("#register-password-err").html(response.errmsg)
                $("#register-password-err").show()
            }
        }

    })

    })
})

var imageCodeId = ""

// TODO 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    //浏览器发起图片验证码请求/image_code?imageCodeId=xxxx
    imageCodeId = generateUUID() //UUID生成图片验证码的编号

    //合成url
    var url="/passport/image_code?imageCodeId="+imageCodeId

    // 给指定img标签设置src, 设置src后img标签会自动向这个url请求这个图片
    $(".get_pic_code").attr("src",url)

}

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".get_code").removeAttr("onclick");
    var mobile = $("#register_mobile").val();
    if (!mobile) {
        $("#register-mobile-err").html("请填写正确的手机号！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err").html("请填写验证码！");
        $("#image-code-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO 发送短信验证码
    var params = {
        // 三个参数 手机号 验证码  验证码编号
        "mobile":mobile,
        "image_code":imageCode,
        "image_code_id": imageCodeId
    }


    // 发起注册请求
    $.ajax({
        //请求地址
        url:"/passport/sms_code",
        // 请求方式
        type:"POST",
        // 请求参数 JSON 要大写
        data:JSON.stringify(params),
        //请求参数的数据类型
        contentType:"application/json",

        success:function (response) {
            if(response.errno == "0"){
                //代表发送成功
                var num = 60 //倒计时60秒\
                //创建计时器,设置倒计时时间
                var t = setInterval(function () {
                    if (num == 1){
                        //代表倒计时结束
                        //清除计时器
                        clearInterval(t)

                        //设置显示内容,倒计时时间结束后再次显示电机获取验证码
                        $(".get_code").html("点击获取验证码")

                        //添加点击事件,因为上面点击过后就把电机事件移除了,
                        // 所以在此处从新添加点击时间
                        $(".get_code").attr("onclick", "sendSMSCode();")

                    }else {
                      num -= 1
                        // 设置a标签显示的内容
                        $(".get_code").html(num+"秒")
                        //显示倒计时时间
                    }
                }, 1000)
            }else{
                //代表发送失败
                alert(response.errmsg)
                //第三方短信发送失败,在此处重新添加点击事件
                $(".get_code").attr("onclick","sendSMSCode();")

            }
        }

    })

}
function logout() {
    $.get('/passport/logout',function (resp) {
        if (resp.errno == 0){
            location.reload()
        }

    })

}




// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num){
	var $frame = $('#main_frame');
	$frame.css({'height':num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    //UUID生成一个8-4-4-16的一个随机字符串并返回
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid; // 返回随机字符串
}
