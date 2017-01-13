# -*- encoding: utf-8 -*-
from django.conf.urls import url

from .views import CourseListView
_author_ = 'shishengjia'
_date_ = '13/01/2017 16:17'


urlpatterns = [
    url(r'^list/$', CourseListView.as_view(), name="course_list"),
]
