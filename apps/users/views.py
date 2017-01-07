# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.http import  HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.base import View
from .models import UserProfile, EmailVerifyCode
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
from utils.email_send import send_email


class CustomBackend(ModelBackend):
    # 在这里重写authenticate方法，实现自定义的校验功能，比如可以邮箱或用户名登陆
    # 注意这里的username既可以代表用户名，也可以代表邮箱
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class ActiveUserView(View):  # ----激活用户----
    def get(self, request, active_code):
        # 从get请求中提取出url包含的active_code寻找对应存有该active_code的邮箱
        all_records = EmailVerifyCode.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                # 根据邮箱查找用户，并将激活状态置为True
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


class RegisterView(View):  # ----注册----
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {"register_form": register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        # 验证数据格式是否合法
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            # 验证邮箱好是否已被注册
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "该邮箱已被注册"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()
            # 用户保存到数据库后，发送激活链接
            send_email(user_name, "register")
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class LoginView(View):  # ----登陆----
    def get(self, request):
         return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        # 验证数据格式是否合法
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            # 这里的authenticate方法实际调用的是上面CustomBackend类里的authenticate方法
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:  #
                if user.is_active:  # 用户是否处于激活状态
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "用户未激活！"})
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误！"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class ForgetPwdView(View):  # ----忘记密码----
    def get(self, request):
        # 需要将forget_form传到忘记密码页面，因为它带有验证码生成
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        # 判断邮箱和验证码是否填写正确,正确则跳转到成功页面，否则继续跳转到该页面（注意也要带上forget_form）
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_email(email, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})

'''
注意下面两个view，分别只处理get和post请求,因为不同请求进入该页面的url格式不一样
ResetView负责处理用户在点击重置密码链接后的请求，带有验证字符串
ModifyPwdView负责处理用户在提交重置密码后的请求，不带有验证字符串
'''


class ResetView(View):  # ----重置密码请求----
    def get(self, request, active_code):
        # 从get请求中提取出url中包含的active_code寻找对应存有该active_code的邮箱
        all_records = EmailVerifyCode.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


class ModifyPwdView(View):  # ----修改密码----
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd = request.POST.get("password", "")
            pwd_again = request.POST.get("password_again", "")
            email = request.POST.get("email", "")
            if pwd != pwd_again: # 两次密码是否一致
                return render(request, "password_reset.html", {"email": email, "msg": "两次密码不一致"})
            # 根据email找到用户，修改密码并保存,返回登陆页面
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd_again)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": "modify_form"})