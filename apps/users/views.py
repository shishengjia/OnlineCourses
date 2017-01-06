# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate,login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import UserProfile
# Create your views here.

# 在这里重写authenticate方法，实现自定义的功能，比如可以邮箱或用户名登陆


class CustomBackend(ModelBackend):
    # 注意这里的username既可以代表用户名，也可以代表邮箱
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


def user_login(request):
    if request.method == "POST":
        user_name = request.POST.get("username", "")
        pass_word = request.POST.get("password", "")
        # 这里的authenticate方法实际调用的是上面CustomBackend类里的authenticate方法
        user = authenticate(username=user_name, password=pass_word)
        if user is not None:
            login(request, user)
            return render(request, "index.html")
        else:
            return render(request, "login.html", {"msg": "用户名或密码错误!"})
    elif request.method == "GET":
        return render(request, "login.html", {})
