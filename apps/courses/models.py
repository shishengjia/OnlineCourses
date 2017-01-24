# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

from DjangoUeditor.models import UEditorField

from organisation.models import CourseOrg, Teacher


class CourseType(models.Model):
    name = models.CharField(max_length=20, verbose_name=u"课程类别")
    add_time = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = u"课程类别"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class Course(models.Model):
    org = models.ForeignKey(CourseOrg, verbose_name=u"课程所属机构", null=True, blank=True, default="1")
    teacher = models.ForeignKey(Teacher, verbose_name=u"课程讲师",  null=True, blank=True)
    type = models.ForeignKey(CourseType, verbose_name=u"课程类别", null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    # TextField不限定长度
    details = UEditorField(verbose_name=u"课程详情", width=600, height=300, imagePath="course/detail_image/",
                           filePath="course/detail_image/", default="")
    level = models.CharField(choices=(("primary", u"初级"), ("middle", u"中级"), ("advanced", u"高级")), max_length=10,
                             verbose_name=u"难度")
    learning_time = models.IntegerField(default=0, verbose_name=u"学习时长（分钟）")
    student_nums = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(upload_to="course/%Y/%m", verbose_name=u"课程封面")
    click_nums = models.IntegerField(default=0, verbose_name=u"点击量")
    notice = models.CharField(max_length=200, verbose_name=u"课前需知", default="")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程信息"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

    def get_course_lesson(self):
        # 获取课程章节
        return self.lesson_set.all()

    def get_course_resources(self):
        return self.courseresource_set.all()

    def get_lesson_num(self):
        return self.lesson_set.all().count()
    get_lesson_num.short_description = "章节数"


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名称")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

    def get_lesson_videos(self):
        # 获取章节下所有视频
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节")
    name = models.CharField(max_length=100, verbose_name=u"视频名称")
    learning_time = models.IntegerField(default=0, verbose_name=u"学习时长（分钟）")
    url = models.CharField(max_length=500, default="", verbose_name=u"视频地址")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name=u"资源文件", max_length=100)

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name
