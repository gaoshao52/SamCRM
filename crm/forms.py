#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author: Gao Shao Yang

from django.forms import ModelForm
from crm import models

class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):

        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

        return ModelForm.__new__(cls)

    class Meta:
        model = models.Enrollment
        fields = ['enrolled_class', 'consultant']

class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):

        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls)

    def clean_qq(self):  # 防止用户在页面修改qq
        if self.instance.qq != self.cleaned_data["qq"]:
            self.add_error("qq", "傻逼敢黑我")
        return self.instance.qq

    def clean_consultant(self):  # 防止用户在页面修改consultant

        return self.instance.consultant

    def clean_source(self):   # 防止用户在页面修改source

        return self.instance.source

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ['tags', 'content', 'memo', 'status', 'referral_from', 'consult_course']
        readonly_fields = ['qq', 'consultant', 'source']


class PaymentForm(ModelForm):
    def __new__(cls, *args, **kwargs):

        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls)

    def clean_amount(self):

        print("cleaned_data['anount']", self.cleaned_data['amount'])
        if int(self.cleaned_data['amount']) < 500:
            self.add_error("amount","费用不能少于500元")
        else:
         return self.cleaned_data['amount']


    class Meta:
        model = models.Payment
        fields = "__all__"
        readonly_fields = ['customer', 'course', 'consultant']
