# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from pure_pagination import Paginator, PageNotAnInteger

from .models import CourseType, Course
from operation.models import UserFavorite, CourseComment
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


class CourseDetailView(View):
    def get(self, request, course_id):

        fav_id = request.POST.get("fav_id", 0)
        fav_type = request.POST.get("fav_type", 0)

        course = Course.objects.get(id=course_id)

        # 判断课程和机构是否已被用户收藏
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.id), fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.org.id), fav_type=2):
                has_fav_org = True


        # 课程点击数加1
        course.click_nums += 1
        course.save()

        type_id = course.type_id

        recommend_course = Course.objects.filter(type_id=type_id)[1:2]

        # 课程章节数
        lesson_num = course.lesson_set.all().count()

        # 课程所属机构教师数量
        teacher_num = course.org.teacher_set.all().count()

        # 课程所属机构课程数
        course_num = course.org.course_set.all().count()

        return render(request, "course-detail.html",{
            "course": course,
            "lesson_num": lesson_num,
            "teacher_num": teacher_num,
            "course_num": course_num,
            "recommend_course": recommend_course,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org
        })


class CourseInfoView(View):
    """
    课程章节信息
    """
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        return render(request, "course-video.html", {
            "course": course
        })


class CourseCommentView(View):
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        comments = CourseComment.objects.filter(course_id=course_id).order_by("-add_time")
        return render(request, "course-comment.html", {
            "course": course,
            "comments": comments
        })


class AddCommentView(View):
    def post(self,request):

        # 判断用户是否登陆
        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail","msg": "用户未登陆"}',
                                content_type="application/json")

        course_id = request.POST.get("course_id", 0)
        comment = request.POST.get("comment", "")
        if int(course_id) > 0 and comment:
            course_comment = CourseComment()
            course_comment.user = request.user
            course_comment.course = Course.objects.get(id=int(course_id))
            course_comment.comment = comment
            course_comment.save()
            return HttpResponse('{"status": "success","msg": "添加成功"}',
                                content_type="application/json")
        else:
            return HttpResponse('{"status": "fail","msg": "添加失败"}',
                                content_type="application/json")


