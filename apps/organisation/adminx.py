# -*- encoding: utf-8 -*-

from .models import CityDict, CourseOrg, Teacher

import xadmin

_author_ = 'shishengjia'
_date_ = '05/01/2017 13:36'


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'add_time']


class CourseOrgAdmin(object):
    list_display = ['name', 'get_course_nums', 'desc', 'category', 'click_num', 'fav_num', 'image', 'address', 'add_time', 'city']
    search_fields = ['name', 'desc', 'category',  'click_num', 'fav_num', 'image', 'address', 'city']
    list_filter = ['name', 'desc', 'category', 'click_num', 'fav_num', 'image', 'address', 'add_time', 'city__name']
    # 其他表以机构为外键时，选择的时候不会加载出所有机构，而是出现搜索框让用户自己进行搜索
    relfield_style = 'fk-ajax'


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company', 'click_num', 'fav_num', 'add_time']
    search_fields = ['org', 'name', 'work_years', 'work_company', 'click_num', 'fav_num']
    list_filter = ['org__name', 'name', 'work_years', 'work_company', 'click_num', 'fav_num', 'add_time']


xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)
