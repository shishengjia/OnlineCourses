# -*- encoding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile
_author_ = 'shishengjia'
_date_ = '06/01/2017 13:57'


class LoginForm(forms.Form):
    """
    登陆表单验证
    名称和html页面的字段名称必须相同
    """
    username = forms.CharField(required=True, error_messages={'required': '用户名/邮箱不能为空'})
    password = forms.CharField(required=True, min_length=6, error_messages={'required': '密码不能为空',
                                                                            'min_length': '密码不能少于6位'})


class RegisterForm(forms.Form):
    """
    注册表单验证
    名称和html页面的字段名称必须相同
    """
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6, error_messages={'required': '密码不能为空',
                                                                            'min_length': '密码不能少于6位'})
    captcha = CaptchaField(required=True, error_messages={"invalid": "验证码错误", "required": "请填写验证码"})


class ForgetForm(forms.Form):
    """
    忘记密码表单验证
    名称和html页面的字段名称必须相同
    """
    email = forms.EmailField(required=True)
    captcha = CaptchaField(required=True, error_messages={"invalid": "验证码错误", "required": "请填写验证码"})


class ModifyPwdForm(forms.Form):
    """
    修改密码表单验证
    名称和html页面的字段名称必须相同
    """
    password = forms.CharField(required=True, min_length=6)
    password_again = forms.CharField(required=True, min_length=6)


class ModifyUserImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']  # 需要验证的字段


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nickName', 'birthday', 'gender', 'address', 'mobile']


