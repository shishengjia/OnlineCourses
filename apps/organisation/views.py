# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import CourseOrg, CityDict
# Create your views here.


class OrgView(View):
    def get(self, request):
        all_org = CourseOrg.objects.all()
         # 根据点击量筛选出所有机构中热度排名前三的机构
        hot_org = all_org.order_by("-click_num")[:3]

        all_city = CityDict.objects.all()

        # 注意，虽然在model里定义的是city字段，但是在数据库中实际上是city_id(这是对外键的一种处理)
        # 默认为空，表示选取所有机构
        city_id = request.GET.get("city", "")
        if city_id:
            all_org = all_org.filter(city_id=city_id)

        # 根据机构类别筛选
        category = request.GET.get("ct", "")
        if category:
            all_org = all_org.filter(category=category)


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
            "hot_org": hot_org,
            "sort": sort
         })

