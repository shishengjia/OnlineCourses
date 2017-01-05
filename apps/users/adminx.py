# -*- encoding: utf-8 -*-

import xadmin
from .models import EmailVerifyCode, Banner

_author_ = 'shishengjia'
_date_ = '04/01/2017 20:21'


class EmailVerifyCodeAdmin(object):
    # 配置xadmin后台管理验证码部分的显示格式
    list_display = ['email', 'code', 'send_type', 'send_time']
    # 配置xadmin后台管理验证码部分的搜索
    search_fields = ['email', 'code', 'send_type']
    list_filter = ['email', 'code', 'send_type', 'send_time']


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


# 将model注册到xadmin的后台
xadmin.site.register(EmailVerifyCode, EmailVerifyCodeAdmin)
xadmin.site.register(Banner, BannerAdmin)
