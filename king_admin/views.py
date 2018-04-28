from django.shortcuts import render, redirect
import importlib
from king_admin import king_admin
from django.core.paginator import Paginator
from django.urls import reverse
from king_admin import forms

from king_admin import utils
# Create your views here.


def index(request):
    print(king_admin.enabled_admins)
    '''
    {'crm': {
        'customerfollowup': <class 'king_admin.king_admin.CustomerFollowUpAdmin'>, 
        'customer': <class 'king_admin.king_admin.CustomerAdmin'>
        }
    }
    '''
    return render(request, "king_admin/table_index.html", {'table_list': king_admin.enabled_admins})


def display_table_objs(request, app_name, table_name):
    '''展示某一张表的数据'''
    # print("--->", app_name, table_name)
    # models_module = importlib.import_module('%s.models'%app_name)

    admin_class = king_admin.enabled_admins[app_name][table_name]


    # object_list = admin_class.model.objects.all()
    object_list, filer_condition = utils.table_filter(request, admin_class)  # 获取过滤数据

    object_list = utils.table_search(request, admin_class, object_list)

    object_list, orderby_key = utils.table_sort(request, admin_class, object_list)  # 获取排序数据




    paginator = Paginator(object_list, admin_class.list_per_page)  # Show 25 contacts per page

    page = request.GET.get('page')  # 获取page number

    query_sets = paginator.get_page(page)  # 同时具有querysets 和page 的方法



    return render(request, "king_admin/table_objs.html", {'admin_class': admin_class,
                                                          "query_sets": query_sets,
                                                          "filer_condition": filer_condition,
                                                          "orderby_key": orderby_key,
                                                          "previous_orderby": request.GET.get("o", ""),
                                                          "search_text": request.GET.get("_q", ""),
                                                          })


def table_obj_change(request, app_name, table_name, obj_id):
    '''修改客户信息'''
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = forms.create_model_form(request, admin_class)  # 获取生成的ModelForm类

    obj = admin_class.model.objects.get(id=obj_id)

    if request.method == "POST":
        form_obj = model_form_class(request.POST, instance=obj)  # 更新
        if form_obj.is_valid():  #检查格式
            form_obj.save()   # 更新到数据库

    else:
        form_obj = model_form_class(instance=obj)

    return render(request, "king_admin/table_obj_change.html", {"form_obj": form_obj,
                                                                "admin_class": admin_class,
                                                                "app_name": app_name,
                                                                "table_name": table_name,
                                                                })

def table_obj_add(request, app_name, table_name):
    '''添加客户信息'''
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = forms.create_model_form(request, admin_class)  # 获取生成的ModelForm类
    form_obj = model_form_class()

    if request.method == "POST":
        form_obj = model_form_class(request.POST)  # 更新
        if form_obj.is_valid():  # 检查格式
            form_obj.save()  # 更新到数据库
            print(reverse("table_objs", args=(app_name, table_name)))
            return redirect(reverse("table_objs", args=(app_name, table_name)))


    return render(request, "king_admin/table_obj_add.html", {"form_obj": form_obj, "admin_class": admin_class})


def table_obj_delete(request, app_name, table_name, obj_id):
    '''删除客户数据'''
    admin_class = king_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)

    return render(request, "king_admin/table_obj_delete.html", {"obj": obj,
                                                                "admin_class": admin_class})
