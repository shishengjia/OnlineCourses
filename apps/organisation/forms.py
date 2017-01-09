# -*- encoding: utf-8 -*-

from django import forms
from operation.models import UserAsk

import re
_author_ = 'shishengjia'
_date_ = '09/01/2017 10:32'


class UserAskForm(forms.ModelForm):  # 通过使用ModeForm来完成表单的验证,相比继承Form代码更简洁
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']  # 需要验证的字段

    def clean_mobile(self):  # 验证手机号是否合法，注意函数名格式 clean_ 加字段
        mobile = self.cleaned_data["mobile"]
        REGEX_MOBILE = "^1[34578]\d{9}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码格式有误", code = "mobile_invalid")