from django.conf.urls import url,include
from django.contrib import admin
from app01 import views

urlpatterns = [
    #user_site 个人站点 condition查询条件（分类、标签、归档时间)、分类名称（java/2019）
    url(r'^cooment_tree/',views.comment_tree),
    url(r'^(?P<site>\w+)/article/(?P<condition>category|tag|date)/(?P<para>.*)/',views.homesite_query),
    url(r'^(?P<article_type_id>\d+)/',views.index),

]
