# -*- encoding: utf-8 -*-
from django.conf.urls import url

from .views import UserInfoView, ModifyUserImageView, UpdatePwdView
_author_ = 'shishengjia'
_date_ = '19/01/2017 20:38'

urlpatterns = [
        url(r'^info/$', UserInfoView.as_view(), name="user_info"),
        url(r'^modify_image/$', ModifyUserImageView.as_view(), name="user_modify_image"),
        url(r'^update_pwd/$', UpdatePwdView.as_view(), name="user_update_pwd"),
]
