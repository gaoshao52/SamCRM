from django.shortcuts import render
import importlib
from king_admin import king_admin
from django.core.paginator import Paginator

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

    # print("--->", app_name, table_name)
    # models_module = importlib.import_module('%s.models'%app_name)

    admin_class = king_admin.enabled_admins[app_name][table_name]


    # object_list = admin_class.model.objects.all()
    object_list, filer_condition = utils.table_filter(request, admin_class)
    print(object_list)
    paginator = Paginator(object_list, admin_class.list_per_page)  # Show 25 contacts per page

    page = request.GET.get('page')
    query_sets = paginator.get_page(page)  # 同事具有querysets 和page 的方法



    return render(request, "king_admin/table_objs.html", {'admin_class': admin_class,
                                                          "query_sets": query_sets,
                                                          "filer_condition": filer_condition,
                                                          })