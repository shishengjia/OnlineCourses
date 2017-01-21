# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.base import View

from pure_pagination import Paginator, PageNotAnInteger

from .models import UserProfile, EmailVerifyCode
from operation.models import UserFavorite, UserCourse, UserMessage
from organisation.models import CourseOrg, Teacher
from courses.models import Course
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, ModifyUserImageForm, UserInfoForm
from utils.email_send import send_email
from utils.LoginJudge import LoginRequiredMixin
import json


class CustomBackend(ModelBackend):
    """
    在这里重写authenticate方法，实现自定义的校验功能，比如可以邮箱或用户名登陆
    注意这里的username既可以代表用户名，也可以代表邮箱
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class ActiveUserView(View):
    """
    激活用户
    """
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


class RegisterView(View):
    """
    注册
    """
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
            send_email(user_name, "register", 16)
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class LoginView(View):
    """
    登陆
    """
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
            if user is not None:  # 用户名或密码是否正确
                if user.is_active:  # 用户是否处于激活状态
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "用户未激活！"})
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误！"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class ForgetPwdView(View):
    """
    忘记密码
    """
    def get(self, request):
        # 需要将forget_form传到忘记密码页面，因为它带有验证码生成
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        # 判断邮箱和验证码是否填写正确,正确则跳转到成功页面，否则继续跳转到该页面（注意也要带上forget_form）
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_email(email, "forget", 16)
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})

'''
注意下面两个view，分别只处理get和post请求,因为不同请求进入该页面的url格式不一样
ResetView负责处理用户在点击重置密码链接后的请求，带有验证字符串
ModifyPwdView负责处理用户在提交重置密码后的请求，不带有验证字符串
'''


class ResetView(View):
    """
    重置密码(用于验证)
    """
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


class ModifyPwdView(View):
    """
    重置密码(未登陆状态)
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd = request.POST.get("password", "")
            pwd_again = request.POST.get("password_again", "")
            email = request.POST.get("email", "")
            if pwd != pwd_again:  # 两次密码是否一致
                return render(request, "password_reset.html", {"email": email, "msg": "两次密码不一致"})
            # 根据email找到用户，修改密码并保存,返回登陆页面
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd_again)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": "modify_form"})


class UserInfoView(LoginRequiredMixin, View):
    """
    用户个人信息显示和修改
    """
    def get(self, request):
        current_page = "info"
        return render(request, "usercenter-info.html", {
            "current_page": current_page
        })

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status": "success"}', content_type="application/json")
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type="application/json")


class ModifyUserImageView(View):
    """
    修改用户头像
    """
    def post(self, request):
        modify_user_image_form = ModifyUserImageForm(request.POST, request.FILES, instance=request.user)
        if modify_user_image_form.is_valid():
            modify_user_image_form.save() # 内置方法，直接进行保存
            return HttpResponse('{"status": "success"}', content_type="application/json")
        else:
            return HttpResponse('{"status": "fail"}', content_type="application/json")


class UpdatePwdView(LoginRequiredMixin, View):
    """
    更新密码(登陆状态)
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd = request.POST.get("password", "")
            pwd_again = request.POST.get("password_again", "")
            if pwd != pwd_again:  # 两次密码是否一致
                return HttpResponse('{"status": "fail", "msg": "两次密码不一致"}', content_type="application/json")
            # 根据email找到用户，修改密码并保存,返回登陆页面
            user = request.user
            user.password = make_password(pwd_again)
            user.save()
            return HttpResponse('{"status": "success"}', content_type="application/json")
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type="application/json")


class SendVerifyCodeView(LoginRequiredMixin, View):
    """
    修改邮箱的验证码
    """
    def get(self, request):
        email = request.GET.get("email", "")
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"msg": "邮箱已经存在"}', content_type="application/json")
        send_email(email, "update_email", 6)
        return HttpResponse('{"status": "success"}', content_type="application/json")


class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改邮箱
    """
    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")
        exit_record = EmailVerifyCode.objects.filter(email=email, code=code, send_type="update_email")
        if exit_record:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type="application/json")
        else:
            return HttpResponse('{"msg": "验证码错误"}', content_type="application/json")


class UserCourseView(LoginRequiredMixin, View):
    """
    用户正在学的课程
    """
    def get(self, request):
        current_page = "course"
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses": user_courses,
            "current_page": current_page
        })


class UserFavOrgView(LoginRequiredMixin, View):
    """
    用户收藏的机构
    """
    def get(self, request):
        current_page = "fav"
        orgs_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        # 从机构收藏对象取出机构ID，根据ID找到机构对象，存入集合
        for fav_org in fav_orgs:
            fav_org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=fav_org_id)
            orgs_list.append(org)

        return render(request, "usercenter-fav-org.html", {
            "orgs_list": orgs_list,
            "current_page": current_page
        })


class UserFavCourseView(LoginRequiredMixin, View):
    """
    用户收藏的课程
    """
    def get(self, request):
        current_page = "fav"
        courses_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        # 从课程收藏对象取出课程ID，根据ID找到课程对象，存入集合
        for fav_course in fav_courses:
            fav_course_id = fav_course.fav_id
            course = Course.objects.get(id=fav_course_id)
            courses_list.append(course)

        return render(request, "usercenter-fav-course.html", {
            "courses_list": courses_list,
            "current_page": current_page
        })


class UserFavTeacherView(LoginRequiredMixin, View):
    """
    用户收藏的讲师
    """
    def get(self, request):
        current_page = "fav"
        teachers_list = []
        # 教师收藏对象
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3,)
        # 从教师收藏对象取出教师ID，根据ID找到教师对象，存入集合
        for fav_teacher in fav_teachers:
            fav_teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=fav_teacher_id)
            teachers_list.append(teacher)

        return render(request, "usercenter-fav-teacher.html", {
            "teachers_list": teachers_list,
            "current_page": current_page
        })


class UserSystemMessageView(LoginRequiredMixin, View):
    """
    用户收到的系统消息列表
    """
    def get(self, request):
        # todo 记得将消息的详情页做一下

        current_page = "sys_message"
        all_sys_messages = UserMessage.objects.filter(user=request.user.id).order_by("-add_time")

        #  分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_sys_messages, per_page=4, request=request)
        sys_messages = p.page(page)
        return render(request, "usercenter-message.html", {
            "sys_messages": sys_messages,
            "current_page": current_page
        })
