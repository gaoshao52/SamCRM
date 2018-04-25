from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta
from django.urls import reverse
register = template.Library()

@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(request, obj, admin_class):
    data_list = []
    for index, column in enumerate(admin_class.list_display):
        field_obj = obj._meta.get_field(column)  # 判断字段是否为choices 类型
        if field_obj.choices:
            col_data = getattr(obj, "get_%s_display"%column)()
        else:
            col_data = getattr(obj, column)

        if type(col_data).__name__ == "datetime":  # 格式化时间
            col_data = col_data.strftime("%Y-%m-%d %H:%M:%S")

        if index == 0:  # add a tag in first column
            col_data = '''<a href="{request_path}{obj_id}/change/">{data}</a>'''.format(
                request_path=request.path,
                obj_id=obj.id,
                data=col_data
            )

        data_list.append("<td>%s</td>"%col_data)
    # print("".join(data_list))
    return mark_safe("".join(data_list))


@register.simple_tag
def render_page_ele(loop_counter, query_sets, filer_condition):
    '''生成分页标签'''
    filter = ""
    for k, v in filer_condition.items():
        filter += "&%s=%s"%(k, v)

    ret = ""
    if abs(query_sets.number - loop_counter) <=1 and abs(query_sets.number - loop_counter) > 0:
        ret = '''<li><a href="?page=%s%s">%s</a></li>'''%(loop_counter,filter ,loop_counter)
    if abs(query_sets.number - loop_counter) ==0:
        ret = '''<li class="active"><a href="?page=%s%s">%s</a></li>'''%(loop_counter,filter ,loop_counter)
    return mark_safe(ret)

@register.simple_tag
def render_filter_ele(condtion, admin_class, filer_condition):
    '''生成过滤标签'''
    select_ele = '''<select class='form-control' name='{filter_field}'><option value=''>----</option>'''
    field_obj = admin_class.model._meta.get_field(condtion)

    selected = ""

    # 判断是否为choices
    if field_obj.choices:
        for choive_item in field_obj.choices:
            if filer_condition.get(condtion) == str(choive_item[0]):
                selected = "selected"
            select_ele += '''<option %s value='%s'>%s</option>'''%(selected, choive_item[0], choive_item[1])
            selected = ""
            select_ele = select_ele.format(filter_field=condtion)

    # 判断是否为外键
    if type(field_obj).__name__ == "ForeignKey":
        for choive_item in field_obj.get_choices()[1:]:
            if filer_condition.get(condtion) == str(choive_item[0]):
                selected = "selected"
            select_ele += '''<option %s value='%s'>%s</option>''' % (selected, choive_item[0], choive_item[1])
            selected = ""
            select_ele = select_ele.format(filter_field=condtion)

    # 判断是否为 DateTimeField
    if type(field_obj).__name__ == "DateTimeField":
        date_els = []
        today_els = datetime.now().date()
        date_els.append(['今天', today_els])
        date_els.append(['昨天', today_els - timedelta(days=1)])
        date_els.append(['近7天', today_els - timedelta(days=7)])
        date_els.append(['本月', today_els.replace(day=1)])
        date_els.append(['近30天', today_els - timedelta(days=30)])
        date_els.append(['近90天', today_els - timedelta(days=90)])
        date_els.append(['近180天', today_els - timedelta(days=180)])
        date_els.append(['本年', today_els.replace(month=1, day=1)])
        date_els.append(['近一年', today_els - timedelta(days=356)])

        selected = ""
        for item in date_els:
            select_ele += '''<option %s value='%s'>%s</option>''' % (selected, item[1], item[0])

        date_name = "%s__gte"%condtion
        select_ele = select_ele.format(filter_field=date_name)

    select_ele += "</select>"
    return mark_safe(select_ele)


@register.simple_tag
def build_paginators(query_sets, filer_condition, previous_orderby, search_text):
    '''生成整个分页'''

    ret = ''

    add_dot_ele = False

    filter = ""

    active = ""

    for k, v in filer_condition.items():
        filter += "&%s=%s" % (k, v)

    for loop_counter in query_sets.paginator.page_range:

        if loop_counter <=2 or loop_counter> query_sets.paginator.num_pages -2 \
            or abs(query_sets.number - loop_counter) <=1:

            if query_sets.number == loop_counter:
                add_dot_ele = False
                active = "active"

            ret += '''<li class="%s"><a href="?page=%s%s&o=%s&_q=%s">%s</a></li>''' % (active, loop_counter, filter, previous_orderby,search_text,loop_counter)
            active = ""


        else:
            if not add_dot_ele:
                ret += '''<li><a>...</a></li>'''
                add_dot_ele = True

    return mark_safe(ret)

@register.simple_tag
def build_table_header_column(column, orderby_key ,filer_condition):
    ele = '''<th><a href="?o={orderby_key}&{filter}">{column}</a>{iron}</th>'''
    iron = ""
    filter = ""
    for k, v in filer_condition.items():
        filter += "&%s=%s" % (k, v)

    if (not orderby_key) or orderby_key.strip("-") != column:  #
        '''
        如果orderby_key 为空值  或者 与column不一样， 就赋予 column值,
        反过来说，只有在 orderby_key 与 column 相等，a 的href才替换
        '''
        orderby_key = column
        iron = ""
    else:
        if orderby_key.startswith("-"):
            iron = '''<span class="glyphicon glyphicon-chevron-up"></span>'''
        else:
            iron = '''<span class="glyphicon glyphicon-chevron-down"></span>'''

    return mark_safe(ele.format(orderby_key=orderby_key, column=column, iron=iron, filter=filter))


@register.simple_tag
def get_model_name(admin_class):
    '''生成表名'''
    return admin_class.model._meta.verbose_name

