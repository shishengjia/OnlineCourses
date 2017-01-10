# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, PageNotAnInteger
from django.http import HttpResponse

from .models import CourseOrg, CityDict
from .forms import UserAskForm
from operation.models import UserFavorite


class OrgView(View):
    """
     分页以及筛选
    """
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


class AddUserAskView(View):
    """
    用户咨询提交
    """
    def post(self, request):
        user_ask_from = UserAskForm(request.POST)
        if user_ask_from.is_valid():
            user_ask = user_ask_from.save(commit=True)  # commit为True表明提交到数据库后并commit
            return HttpResponse("{'status': 'success'}", content_type="application/json")
        else:
            return HttpResponse('{"status": "fail","msg": "添加出错"}',
                                content_type="application/json")


class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        current_page = "home"   # 当前页标记
        org = CourseOrg.objects.get(id=org_id)  # 根据url中的org_id查询机构
        all_courses = org.course_set.all()  # 根据course自己生成的’course_set‘字段获取所有课程(前提机构是课程的外键)
        all_teachers = org.teacher_set.all()[:1]  # 同上
        """
        收藏的处理是单独于网页其他部分，采用的是ajax的方式
        整个网页加载刷新的时候，需要判断一下当前机构是否已经被收藏
        下面的机构课程，介绍，讲师也是同样
        """
        has_fav = False
        if request.user.is_authenticated():  # 判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org.id), fav_type=2):
                has_fav = True  # 如果能查询到该记录，则标记为true

        return render(request, "org-detail-homepage.html", {
            "all_courses": all_courses,
            "all_teachers": all_teachers,
            "org": org,
            "current_page": current_page,
            "has_fav": has_fav  # 返回收藏状态，交由html页面处理
        })


class OrgCourseView(View):
    """
    机构课程
    """
    def get(self, request, org_id):
        current_page = "course"
        org = CourseOrg.objects.get(id=org_id)
        all_courses = org.course_set.all()

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org.id), fav_type=2):
                has_fav = True

        return render(request, "org-detail-course.html", {
            "all_courses": all_courses,
            "org": org,
            "current_page": current_page,
            "has_fav": has_fav
        })


class OrgDescView(View):
    """
    机构详情
    """
    def get(self, request, org_id):
        current_page = "desc"
        org = CourseOrg.objects.get(id=org_id)

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org.id), fav_type=2):
                has_fav = True

        return render(request, "org-detail-desc.html", {
            "current_page": current_page,
            "org": org,
            "has_fav": has_fav
        })


class OrgTeacherView(View):
    """
    机构讲师
    """
    def get(self, request, org_id):
        current_page = "teacher"
        org = CourseOrg.objects.get(id=org_id)
        all_teachers = org.teacher_set.all()

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org.id), fav_type=2):
                has_fav = True

        return render(request, "org-detail-teachers.html", {
            "all_teachers": all_teachers,
            "org": org,
            "current_page": current_page,
            "has_fav": has_fav
        })


class AddFavoriteView(View):
    """
    添加收藏,取消收藏
    """
    def post(self, request):
        fav_id = request.POST.get("fav_id", 0)
        fav_type = request.POST.get("fav_type", 0)
        # 判断用户是否登陆
        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail","msg": "用户未登陆"}',
                                content_type="application/json")

        # 查询该记录是否存在，也就是是否被收藏
        exit_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        # 已经收藏，则这次操作为取消收藏
        if exit_records:
            exit_records.delete()
            # 取消收藏，则按钮显示“收藏”
            return HttpResponse('{"status": "fail","msg": "收藏"}',
                                content_type="application/json")
        else:
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav = UserFavorite()
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                return HttpResponse('{"status": "success","msg": "已收藏"}',
                                    content_type="application/json")
            else:
                return HttpResponse('{"status": "fail","msg": "收藏出错"}',
                                    content_type="application/json")



