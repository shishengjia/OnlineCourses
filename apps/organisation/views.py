# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import CourseOrg, CityDict
# Create your views here.


class OrgView(View):
    def get(self, request):
        all_org = CourseOrg.objects.all()
        all_city = CityDict.objects.all()
        org_nums = all_org.count()  # 机构数量
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
            "org_nums": org_nums
        })

