from django.shortcuts import render, redirect, HttpResponse
import importlib
from king_admin import king_admin
from django.core.paginator import Paginator
from django.urls import reverse
from king_admin import forms
from king_admin import utils
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
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

@login_required()
def display_table_objs(request, app_name, table_name):
    '''展示某一张表的数据'''
    # print("--->", app_name, table_name)
    # models_module = importlib.import_module('%s.models'%app_name)
    # import time
    # time.sleep(5)

    admin_class = king_admin.enabled_admins[app_name][table_name]

    if request.method == "POST":   # action 来了
        print(request.POST)
        selected_ids = request.POST.get("selected_ids")

        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(","))
        else:
            raise KeyError("No selected object id")

        print(selected_objs)
        action = request.POST.get("action")

        if hasattr(admin_class, action):
            action_func = getattr(admin_class, action)
            request._admin_action = action  # 给king_admin 中的删除action
            return action_func(admin_class, request, selected_objs)



        return HttpResponse("action submit")


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

@login_required
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

@login_required
def table_obj_add(request, app_name, table_name):
    '''添加客户信息'''
    admin_class = king_admin.enabled_admins[app_name][table_name]

    admin_class.is_add_form = True

    model_form_class = forms.create_model_form(request, admin_class)  # 获取生成的ModelForm类
    form_obj = model_form_class()

    if request.method == "POST":
        form_obj = model_form_class(request.POST)  # 更新
        if form_obj.is_valid():  # 检查格式

            print(" new customer data:", form_obj.cleaned_data)
            form_obj.save()  # 更新到数据库
            print(reverse("table_objs", args=(app_name, table_name)))
            return redirect(reverse("table_objs", args=(app_name, table_name)))


    return render(request, "king_admin/table_obj_add.html", {"form_obj": form_obj, "admin_class": admin_class})

@login_required
def table_obj_delete(request, app_name, table_name, obj_id):
    '''删除客户数据'''
    # print("delete==-----%s----%s---%s"%(app_name, table_name, obj_id))
    admin_class = king_admin.enabled_admins[app_name][table_name]
    objs = admin_class.model.objects.filter(id=obj_id)
    errors = {}
    if admin_class.readonly_table:
        errors = {"readonly_table": "table is readonly, obj [%s] cannot be delete"%objs.first()}
    else:
        errors = {}

    print("readonly error:", errors)

    if request.method == "POST":
        if not admin_class.readonly_table:
            objs.first().delete()
            return redirect(reverse("table_objs", args=(app_name, table_name)))


    return render(request, "king_admin/table_obj_delete.html", {"objs": objs,
                                                                "app_name": app_name,
                                                                "table_name": table_name,
                                                                "errors": errors,
                                                                })

@login_required
def password_reset(request, app_name, table_name, obj_id):
    '''修改密码'''
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = forms.create_model_form(request, admin_class)  # 获取生成的ModelForm类

    obj = admin_class.model.objects.get(id=obj_id)

    errors = {}

    if request.method == "POST":
        _password1 = request.POST.get("password1")
        _password2 = request.POST.get("password2")

        if _password1 == _password2:
            obj.set_password(_password1)
            obj.save()

            return redirect(request.path.rstrip("password/"))

        else:
            errors = {'info': "用户名密码不一致"}


    return render(request, "king_admin/password_reset.html", {"obj": obj, "errors": errors})