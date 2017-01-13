# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View

from pure_pagination import Paginator, PageNotAnInteger

from .models import CourseType, Course
# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_course = Course.objects.all()
        hot_course = all_course.order_by("-click_nums")[:3]  # 根据点击量筛选出所有机构中热度排名前三的机构
        all_type = CourseType.objects.all()

        # 注意，虽然在model里定义的是city字段，但是在数据库中实际上是city_id(这是对外键的一种处理)
        # 根据城市筛选，默认为空，表示选取所有机构
        type_id = request.GET.get("type", "")
        if type_id:
            all_course = all_course.filter(type_id=type_id)

        # 根据机构类别筛选
        org_id = request.GET.get("ct", "")
        if org_id:
            all_course = all_course.filter(org_id=org_id)

        # 根据分类（学习人数，热度）来筛选
        sort = request.GET.get("sort", "")
        if sort:
            if sort == "student_nums":
                all_course = all_course.order_by("-student_nums")
            elif sort == "hot":
                all_course = all_course.order_by("-click_nums")


        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_course, per_page=5, request=request)
        courses = p.page(page)

        return render(request, "course-list.html", {
            "all_type": all_type,
            "courses": courses,
            "type_id": type_id,
            "org_id": org_id,
            "hot_course": hot_course,
            "sort": sort
        })
