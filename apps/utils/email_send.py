# -*- encoding: utf-8 -*-
from users.models import EmailVerifyCode
from random import Random
from django.core.mail import send_mail
from OnlineCourses.settings import EMAIL_FROM
_author_ = 'shishengjia'
_date_ = '06/01/2017 20:13'


# 生成随机字符串
def generate_random_str(randomlength=8):
    strs = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        strs += chars[random.randint(0, length)]
    return strs


def send_email(email, send_type="register", code_length=16):
    # 事先将邮箱认证链接末尾的随机字符串保存到数据库中
    email_verify = EmailVerifyCode()
    code = generate_random_str(code_length)
    email_verify.email = email
    email_verify.code = code
    email_verify.send_type = send_type
    email_verify.save()
    # 保存随机字符串后，向该字符串绑定在url后面，向用户发送对应的邮件
    if send_type == "register":
        email_title = "源学网注册激活链接"
        email_body = "请点击下边的连接以激活账号: http://127.0.0.1:8000/active/{0}".format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "forget":
        email_title = "源学网重置密码链接"
        email_body = "请点击下边的连接重置密码: http://127.0.0.1:8000/reset/{0}".format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "update_email":
        email_title = "源学网修改邮箱验证码"
        email_body = "修改邮箱验证码为:{0}".format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass