# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from pure_pagination import Paginator, PageNotAnInteger

from .models import CourseType, Course, Video
from operation.models import UserFavorite, CourseComment, UserCourse
from utils.LoginJudge import LoginRequiredMixin
# Create your views here.


class CourseListView(View):
    """
    课程列表
    """
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

        # 根据分类（学习人数，热度）来排序
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
            "all_type": all_type,  # 所有课程类别
            "courses": courses,  # 课程
            "type_id": type_id,  # 课程类别ID
            "org_id": org_id,    # 课程机构ID
            "hot_course": hot_course, # 热门课程
            "sort": sort  # 排序
        })


class CourseDetailView(View):
    """
    课程详情
    """
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
        # 根据课程类别ID推荐相关课程
        recommend_course = Course.objects.filter(type_id=type_id)[1:2]

        # 课程章节数
        lesson_num = course.lesson_set.all().count()

        # 课程所属机构教师数量
        teacher_num = course.org.teacher_set.all().count()

        # 课程所属机构课程数
        course_num = course.org.course_set.all().count()

        return render(request, "course-detail.html",{
            "course": course,   # 当前课程对象
            "lesson_num": lesson_num,
            "teacher_num": teacher_num,
            "course_num": course_num,
            "recommend_course": recommend_course,  # 推荐课程
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息,继承LoginRequiredMixin类，完成是否登陆的验证，没有登陆跳转到登陆界面
    """
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        course.student_nums += 1
        course.save()
        # 判断该登陆用户是否已经学过这门课，没学过的就添加到记录中
        course_learned = UserCourse.objects.filter(user=request.user, course=course)
        if not course_learned:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 从UserCourse表取出所有课程为当前课程的记录
        users_course = UserCourse.objects.filter(course=course)
        # 从取出的记录中取出记录对应的用户ID(学过该门课的用户的ID)
        users_id = [users_course.user.id for users_course in users_course]
        # 根据ID从UserCourse中找出对应用户学过的所有其他课程的记录（学过该门课的用户学过的其他课程的记录）
        all_users_courses = UserCourse.objects.filter(user_id__in=users_id)
        # 从记录中遍历出相应课程ID（学过该门课的用户学过的其他课程的ID）
        courses_ids = [all_users_course.course.id for all_users_course in all_users_courses]
        # 根据ID找出对应的课程对象，并按热度排名，选出前3名
        relate_courses = Course.objects.filter(id__in=courses_ids).order_by("-click_nums")[:3]

        return render(request, "course-video.html", {
            "course": course,
            "relate_courses": relate_courses
        })


class CourseCommentView(LoginRequiredMixin, View):
    """
    课程评论，继承LoginRequiredMixin类，完成是否登陆的验证，没有登陆跳转到登陆界面
    """
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        comments = CourseComment.objects.filter(course_id=course_id).order_by("-add_time")
        return render(request, "course-comment.html", {
            "course": course,
            "comments": comments
        })


class AddCommentView(View):
    """
    处理添加评论的请求
    """
    def post(self, request):

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


class CourseVideoView(View):
    def get(self, request, video_id):

        video = Video.objects.get(id=int(video_id))

        course = video.lesson.course
        # 判断该登陆用户是否已经学过这门课，没学过的就添加到记录中
        course_learned = UserCourse.objects.filter(user=request.user, course=course)
        if not course_learned:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 从UserCourse表取出所有课程为当前课程的记录
        users_course = UserCourse.objects.filter(course=course)
        # 从取出的记录中取出记录对应的用户ID(学过该门课的用户的ID)
        users_id = [users_course.user.id for users_course in users_course]
        # 根据ID从UserCourse中找出对应用户学过的所有其他课程的记录（学过该门课的用户学过的其他课程的记录）
        all_users_courses = UserCourse.objects.filter(user_id__in=users_id)
        # 从记录中遍历出相应课程ID（学过该门课的用户学过的其他课程的ID）
        courses_ids = [all_users_course.course.id for all_users_course in all_users_courses]
        # 根据ID找出对应的课程对象，并按热度排名，选出前3名
        relate_courses = Course.objects.filter(id__in=courses_ids).order_by("-click_nums")[:3]

        return render(request, "course-play.html", {
            "course": course,
            "relate_courses": relate_courses,
            "video": video
        })


