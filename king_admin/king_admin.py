from crm import models
from django.shortcuts import render, redirect, HttpResponse

enabled_admins = {}
'''
enabled_admins = {'app_name': {'table_name01': admin_class, 'table_name02': admin_class}}
'''

class BaseAdmin(object):
    list_display = []
    list_filters = []
    search_fields = []
    list_per_page = 20
    ordering = None
    filter_horizontal = []
    readonly_fields = []
    readonly_table = False
    actions = ["delete_selected_objs", ]
    modelform_exclude_fields = []

    def delete_selected_objs(self, request, querysets):
        print("delete_selected_objs", self, request, querysets)
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name

        errors = {}
        if self.readonly_table:
            errors = {"readonly_table": "table is readonly,cannot be delete"}
        else:
            errors = {}

        if request.method == "POST" and request.POST.get("delete_comfirm") == "yes":
            if not self.readonly_table:
                querysets.delete()
            return redirect("/king_admin/%s/%s/"%(app_name, table_name))


        selected_ids = ",".join([str(i.id) for i in querysets])
        return render(request, "king_admin/table_obj_delete.html", {"objs": querysets,
                                                                    "app_name": app_name,
                                                                    "table_name": table_name,
                                                                    "selected_ids": selected_ids,
                                                                    "action": request._admin_action,
                                                                    "errors": errors,
                                                                    })

    def default_form_validation(self):
        '''用户可以在此进行自定义的表单验证，相当于 django form的clean方法'''
        pass


class CustomerAdmin(BaseAdmin):
    list_display = ("id", "qq", "name","source", "consultant", "consult_course", "content", "status", "date", "enroll")
    # model = models.Customer
    list_filters = ('source', 'consultant', 'consult_course', 'status', 'date')
    list_per_page = 3
    search_fields = ('qq', 'name', 'consultant__name')
    # ordering = "qq"
    filter_horizontal = ('tags',)
    # readonly_fields = ["qq", "consultant", "tags"]

    # readonly_table = True

    actions = ["delete_selected_objs", "test"]

    def test(self, request, querysets):
        pass

    test.display_name = "测试项"

    def enroll(self): # 增加字段
        '''报名入口'''
        if self.instance.status == 0:
            link_name = "报名"
        else:
            link_name = "报名新课程"
        return "<a href='/crm/customer/%s/enrollment/'>%s</a>"%(self.instance.id, link_name)

    enroll.display_name = "报名链接"


    def default_form_validation(self):
        # print("----------->customer", self )
        # print("----------->instance", self.instance)

        consult_content = self.cleaned_data.get("content", "")

        if len(consult_content) < 15:
            return  self.ValidationError(
                ('Field %(field)s 咨询内容不能少于15个'),
                code="invalid",
                params={
                    'field': "content"
                }
            )
    def clean_name(self):
        print("name clean validation:", self.cleaned_data["name"])
        if not self.cleaned_data.get("name"):
            self.add_error("name", "cannot be null")

        return self.cleaned_data["name"]


    # actions = ["delete_selected_objs", ]
    #
    # def delete_selected_objs(self, request, querysets):
    #     print("delete_selected_objs", self, request, querysets)
    #     app_name = self.model._meta.app_label
    #     table_name = self.model._meta.model_name
    #
    #
    #     if request.method == "POST" and request.POST.get("delete_comfirm") == "yes":
    #         querysets.delete()
    #         return redirect("/king_admin/%s/%s/"%(app_name, table_name))
    #
    #
    #     selected_ids = ",".join([str(i.id) for i in querysets])
    #     return render(request, "king_admin/table_obj_delete.html", {"objs": querysets,
    #                                                                 "app_name": app_name,
    #                                                                 "table_name": table_name,
    #                                                                 "selected_ids": selected_ids,
    #                                                                 "action": request._admin_action,
    #                                                                 })

    # delete_selected_objs.display_name = "删除选中项"



class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('customer', 'consultant', 'date')

class UserProfileAdmin(BaseAdmin):
    list_displays = ('email', 'name')
    readonly_fields = ("password",)
    filter_horizontal = ("user_permissions", "groups")
    modelform_exclude_fields = ['last_login',]

class CourseRecordAdmin(BaseAdmin):
    list_display = ["from_class", "day_num", "teacher", "has_homework","homework_content", "date"]

    def initialize_studyrecords(self, request, queryset):
        print("------>initialize_studyrecords", self, request, queryset)
        if len(queryset) >1:
            return HttpResponse("只能选择一个班级")

        print(queryset[0].from_class.enrollment_set.all())

        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            # models.StudyRecord.objects.get_or_create(
            #     student=enroll_obj,
            #     course_record=queryset[0],
            #     attendance=0,
            #     score=0,
            # )
            new_obj_list.append(models.StudyRecord(
                student=enroll_obj,
                course_record=queryset[0],
                attendance=0,
                score=0,
            ))
        try:
            models.StudyRecord.objects.bulk_create(new_obj_list)
        except Exception as e:
            return HttpResponse("批量创建数据失败。。。。。。。。")
        return redirect("/king_admin/crm/studyrecord/?course_record=%s"%queryset[0].id)

    initialize_studyrecords.display_name = "初始化本节所有的上课记录"
    actions = ["initialize_studyrecords",]


class StudyRecordAdmin(BaseAdmin):
    list_display = ['student','course_record', 'attendance', 'score', 'date']
    list_filters = ['course_record', 'score', 'attendance']




def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}

    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)
register(models.CourseRecord, CourseRecordAdmin)
register(models.StudyRecord, StudyRecordAdmin)

