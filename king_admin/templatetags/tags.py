from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(obj, admin_class):
    data_list = []
    for column in admin_class.list_display:
        field_obj = obj._meta.get_field(column)  # 判断字段是否为choices 类型
        if field_obj.choices:
            col_data = getattr(obj, "get_%s_display"%column)()
        else:
            col_data = getattr(obj, column)

        if type(col_data).__name__ == "datetime":  # 格式化时间
            col_data = col_data.strftime("%Y-%m-%d %H:%M:%S")

        data_list.append("<td>%s</td>"%col_data)
    # print("".join(data_list))
    return mark_safe("".join(data_list))


@register.simple_tag
def render_page_ele(loop_counter, query_sets, filer_condition):
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
    select_ele = '''<select class='form-control' name='%s'><option value=''>----</option>'''%condtion
    field_obj = admin_class.model._meta.get_field(condtion)

    selected = ""

    # 判断是否为choices
    if field_obj.choices:
        for choive_item in field_obj.choices:
            if filer_condition.get(condtion) == str(choive_item[0]):
                selected = "selected"
            select_ele += '''<option %s value='%s'>%s</option>'''%(selected, choive_item[0], choive_item[1])
            selected = ""

    # 判断是否为外键
    if type(field_obj).__name__ == "ForeignKey":
        for choive_item in field_obj.get_choices()[1:]:
            if filer_condition.get(condtion) == str(choive_item[0]):
                selected = "selected"
            select_ele += '''<option %s value='%s'>%s</option>''' % (selected, choive_item[0], choive_item[1])
            selected = ""


    select_ele += "</select>"
    return mark_safe(select_ele)


@register.simple_tag
def build_paginators(query_sets, filer_condition):
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

            ret += '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (active, loop_counter, filter, loop_counter)
            active = ""


        else:
            if not add_dot_ele:
                ret += '''<li><a>...</a></li>'''
                add_dot_ele = True

    return mark_safe(ret)

