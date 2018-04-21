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

