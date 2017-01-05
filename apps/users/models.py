# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


# 用户
class UserProfile(AbstractUser):
    nickName = models.CharField(max_length=50, verbose_name=u"昵称", default="")
    birthday = models.DateField(verbose_name=u"生日", null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", u"女")), default="female")
    address = models.CharField(max_length=100, default="")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to="image/%Y/%m", default=u"image/default.png", max_length=100)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.username


class EmailVerifyCode(models.Model):
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    # 记录是何种类型
    send_type = models.CharField(choices=(("register", u"注册"), ("forget", u"找回密码")), max_length=10,
                                 verbose_name=u"验证码类型")
    # datetime.now()返回model编译时的时间
    # datetime.now 返回model实例化时的时间
    send_time = models.DateTimeField(default=datetime.now, verbose_name=u"发送时间")

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0}({1})'.format(self.code,self.email)


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name=u"标题")
    image = models.ImageField(upload_to="banner/%Y/%m", verbose_name=u"轮播图", max_length=100)
    # 点击图片后的跳转地址
    url = models.URLField(max_length=200, verbose_name=u"访问地址")
    # 控制轮播图的顺序
    index = models.IntegerField(default=100, verbose_name=u"顺序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"轮播图片"
        verbose_name_plural = verbose_name
