from django.db.models import Q

def table_filter(request, admin_class):
    '''过滤数据'''
    filer_condition = {}
    ignore_list = ["page", "o", "_q"]

    for k, v in request.GET.items():
        if k in ignore_list: #
            continue
        if v:
            filer_condition[k] = v

    return admin_class.model.objects.filter(**filer_condition), filer_condition

def table_sort(request, admin_class, obj):
    '''数据排序'''
    orderby_key = request.GET.get("o")
    if orderby_key:
        obj = obj.order_by(orderby_key)
        if orderby_key.startswith("-"):
            orderby_key = orderby_key.strip("-")
        else:
            orderby_key = "-%s"%orderby_key

    return obj, orderby_key

def table_search(request, admin_class, object_list):
    """过滤数据"""
    search_key = request.GET.get("_q", "")
    q_obj = Q()
    q_obj.connector = "OR"
    for column in admin_class.search_fields:
        q_obj.children.append(("%s__contains"%column, search_key))

    ret = object_list.filter(q_obj)

    return ret

