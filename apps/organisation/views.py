# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from .models import CourseOrg, CityDict
from .forms import UserAskForm
# Create your views here.


class OrgView(View):   # 完成分页以及筛选逻辑
    def get(self, request):
        all_org = CourseOrg.objects.all()
        hot_org = all_org.order_by("-click_num")[:3]  # 根据点击量筛选出所有机构中热度排名前三的机构
        all_city = CityDict.objects.all()  # 获取城市列表

        # 注意，虽然在model里定义的是city字段，但是在数据库中实际上是city_id(这是对外键的一种处理)
        # 根据城市筛选，默认为空，表示选取所有机构
        city_id = request.GET.get("city", "")
        if city_id:
            all_org = all_org.filter(city_id=city_id)

        # 根据机构类别筛选
        category = request.GET.get("ct", "")
        if category:
            all_org = all_org.filter(category=category)

        # 根据分类（学习人数，热度）来筛选
        sort = request.GET.get("sort", "")
        if sort:
            if sort == "student_nums":
                all_org = all_org.order_by("-student_nums")
            elif sort == "hot":
                all_org = all_org.order_by("-click_num")

        org_nums = all_org.count()
        #  分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_org, per_page=5, request=request)
        orgs = p.page(page)
        return render(request, "org-list.html", {
            "orgs": orgs,
            "all_city": all_city,
            "org_nums": org_nums,
            "city_id": city_id,    # 将city_id传回页面，方便页面知道中city列表知道哪一个被选中了
            "category": category,   # 同上
            "hot_org": hot_org,     # 返回热度前三的机构
            "sort": sort            # 同city_id
         })


class AddUserAskView(View):  # 用户咨询提交
    def post(self, request):
        user_ask_from = UserAskForm(request.POST)
        if user_ask_from.is_valid():
            user_ask = user_ask_from.save(commit=True)  # commit为True表明提交到数据库后并commit
            return HttpResponse("{'status': 'success'}", content_type="application/json")
        else:
            return HttpResponse('{"status": "fail","msg": "添加出错"}',
                                content_type="application/json")


class OrgHomeView(View):
    def get(self, request, org_id):
        current_page = "home"
        org = CourseOrg.objects.get(id=org_id)
        all_courses = org.course_set.all()
        all_teachers = org.teacher_set.all()[:1]
        return render(request, "org-detail-homepage.html", {
            "all_courses": all_courses,
            "all_teachers": all_teachers,
            "org": org,
            "current_page": current_page
        })


class OrgCourseView(View):
    def get(self, request, org_id):
        current_page = "course"
        org = CourseOrg.objects.get(id=org_id)
        all_courses = org.course_set.all()
        return render(request, "org-detail-course.html", {
            "all_courses": all_courses,
            "org": org,
            "current_page": current_page
        })


class OrgDescView(View):
    def get(self, request, org_id):
        current_page = "desc"
        org = CourseOrg.objects.get(id=org_id)
        return render(request, "org-detail-desc.html", {
            "current_page": current_page,
            "org": org
        })


class OrgTeacherView(View):
    def get(self, request, org_id):
        current_page = "teacher"
        org = CourseOrg.objects.get(id=org_id)
        all_teachers = org.teacher_set.all()
        return render(request, "org-detail-teachers.html", {
            "all_teachers": all_teachers,
            "org": org,
            "current_page": current_page
        })
