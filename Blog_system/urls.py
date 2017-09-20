"""Blog_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from app01.views import *
from app01 import views
from app01 import urls
from django.views.static import serve
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^media/(?P<path>.*)$',serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^index/',index),
    url(r'^$',index),
    url(r'^blog/',include('app01.urls')),
    url(r'^homesite/',include('app01.homesite')),
    url(r'^login/',log_in),
    url(r'^valid_code/',valid_code),
    url(r'^reg/',reg),
    url(r'^poll/',poll),
    url(r'^comment/',comment),
    url(r'^logout/',log_out),
    #---------文章管理URL------------------------------
    url(r'^back_index/$',back_index),
    url(r'^add_article/$',add_article),
    url(r'^upload_file/$',upload_file),
    url(r'^delet_article/$',delet_article),
    url(r'^cbv/$',CBV.as_view()),
]
