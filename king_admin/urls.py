from django.urls import path, include, re_path
from king_admin import views

urlpatterns = [
    re_path(r'^$', views.index, name="table_index"),
    re_path(r'^(\w+)/(\w+)/$', views.display_table_objs, name="table_objs"),
    re_path(r'^(\w+)/(\w+)/(\d+)/change/$', views.table_obj_change, name="table_obj_change"),

]