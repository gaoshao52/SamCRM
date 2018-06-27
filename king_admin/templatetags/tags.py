from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta
from django.urls import reverse
from django.core.exceptions import FieldDoesNotExist
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
    col_data = ""
    for index, column in enumerate(admin_class.list_display):
        try:
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
        except FieldDoesNotExist as e:  # 字段不在数据库，额外增加的字段
            if hasattr(admin_class, column):
                col_func = getattr(admin_class, column)
                admin_class.instance = obj
                col_data = col_func()

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
def build_table_header_column(column, orderby_key ,filer_condition, admin_class):
    try:
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name.upper()


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


        return mark_safe(ele.format(orderby_key=orderby_key, column=column_verbose_name, iron=iron, filter=filter))
    except FieldDoesNotExist as e:
        column_verbose_name = getattr(admin_class, column).display_name.upper()
        return mark_safe('''<th><a href="javascript:void(0);">%s</a></th>'''%column_verbose_name)


@register.simple_tag
def get_model_name(admin_class):
    '''生成表名'''
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_m2m_obj_list(admin_class, field, form_obj):
    '''获取m2m数据对象'''

    all_object_list = getattr(admin_class.model, field.name).rel.model.objects.all()  # 所有的数据对象


    if form_obj.instance.id:

        selected_object_list = getattr(form_obj.instance, field.name).all()  # 用户已选择的数据对象
    else:
        selected_object_list = []
    standby_object_list = []
    for item in all_object_list:
        if item not in selected_object_list:
            standby_object_list.append(item)

    return standby_object_list

@register.simple_tag
def get_m2m_selected_obj_list(form_obj, field):
    '''获取已选择的m2m数据'''

    if form_obj.instance.id:
        select_obj_list = getattr(form_obj.instance, field.name).all()
    else:
        select_obj_list = []

    return select_obj_list


def recursive_related_objs_lookup(objs):
    #model_name = objs[0]._meta.model_name
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = '''<li><span class='btn-link'> %s:</span> %s </li>'''%(obj._meta.verbose_name,obj.__str__().strip("<>"))
        ul_ele += li_ele

        #for local many to many
        ##print("------- obj._meta.local_many_to_many", obj._meta.local_many_to_many)
        for m2m_field in obj._meta.local_many_to_many: #把所有跟这个对象直接关联的m2m字段取出来了
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name) #getattr(customer, 'tags')
            for o in m2m_field_obj.select_related():# customer.tags.select_related()
                li_ele = '''<li> %s: %s </li>''' % (m2m_field.verbose_name, o.__str__().strip("<>"))
                sub_ul_ele +=li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele  #最终跟最外层的ul相拼接


        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():

                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    #print("-------ManyToManyRel",accessor_obj,related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                        target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele ="<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li> <span class='btn-link'>%s</span>: %s </li>''' % (o._meta.verbose_name, o.__str__().strip("<>"))
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj,related_obj.get_accessor_name()): # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj,related_obj.get_accessor_name())
                #上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj,'select_related'): # slect_related() == all()
                    target_objs = accessor_obj.select_related() #.filter(**filter_coditions)
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    #print("one to one i guess:",accessor_obj)
                    target_objs = [accessor_obj]
                #print("target_objs",target_objs)
                if len(target_objs) >0:
                    ##print("\033[31;1mdeeper layer lookup -------\033[0m")
                    #nodes = recursive_related_objs_lookup(target_objs,model_name)
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele +="</ul>"
    return ul_ele


@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    if objs:
        model_class = objs[0]._meta.model
        #mode_name = objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))


@register.simple_tag
def get_action_verbose_name(admin_class, action):
    '''action 函数名显示'''

    action_func = getattr(admin_class, action)

    return action_func.display_name if hasattr(action_func, "display_name") else action


