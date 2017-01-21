# -*- encoding: utf-8 -*-
from django.conf.urls import url

from .views import UserInfoView, ModifyUserImageView, UpdatePwdView, SendVerifyCodeView, UpdateEmailView, \
    UserCourseView, UserFavCourseView, UserFavTeacherView, UserFavOrgView
_author_ = 'shishengjia'
_date_ = '19/01/2017 20:38'

urlpatterns = [
    # 用户信息
    url(r'^info/$', UserInfoView.as_view(), name="user_info"),
    # 修改用户头像
    url(r'^modify_image/$', ModifyUserImageView.as_view(), name="user_modify_image"),
    # 更新密码
    url(r'^update_pwd/$', UpdatePwdView.as_view(), name="user_update_pwd"),
    # 修改邮箱时的验证码
    url(r'^send_verify_code/$', SendVerifyCodeView.as_view(), name="user_send_verify_code"),
    # 修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name="user_update_email"),
    # 修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name="user_update_email"),
    # 我的课程
    url(r'^my_course/$', UserCourseView.as_view(), name="user_my_course"),
    # 我收藏的机构
    url(r'^myfav/org/$', UserFavOrgView.as_view(), name="user_my_fav_org"),
    # 我收藏的教师
    url(r'^myfav/teacher/$', UserFavTeacherView.as_view(), name="user_my_fav_teacher"),
    # 我收藏的课程
    url(r'^myfav/course/$', UserFavCourseView.as_view(), name="user_my_fav_course"),
]
