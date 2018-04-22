from crm import models

enabled_admins = {}
'''
enabled_admins = {'app_name': {'table_name01': admin_class, 'table_name02': admin_class}}
'''

class BaseAdmin(object):
    list_display = []
    list_filters = []
    list_per_page = 20

class CustomerAdmin(BaseAdmin):
    list_display = ("id", "qq", "source", "consultant", "consult_course", "content", "status", "date")
    # model = models.Customer
    list_filters = ('source', 'consultant', 'consult_course', 'status')
    list_per_page = 1

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('customer', 'consultant', 'date')

def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}

    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)


