# -*- encoding: utf-8 -*-

from .models import Course, Lesson, Video, CourseResource

import xadmin

_author_ = 'shishengjia'
_date_ = '05/01/2017 13:02'


class CourseAdmin(object):
    list_display = ['name', 'desc', 'details', 'level', 'learning_time', 'student_nums',
                    'fav_nums', 'image', 'click_nums', 'add_time']
    search_fields = ['name', 'desc', 'details', 'level', 'student_nums',
                     'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'details', 'level', 'learning_time', 'student_nums',
                   'fav_nums', 'image', 'click_nums', 'add_time']


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # 注意搜索外键字段的格式course__字段名
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson__name', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'add_time', 'download']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'add_time', 'download']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
