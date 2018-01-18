from django.conf.urls import url
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as authviews
from . import views
from . import viewslocstar
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls import handler404, handler500

handler404 = views.error_404
#app_name = 'glos'
urlpatterns = [
   
    url(r'^$', views.index, name='index'),
    url(r'^lspsoftware/', views.lspsoftware, name='lspsoftware'),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
    url(r'^create_post/', views.create_post),
    url(r'^edit/(\d+)/$', views.editentry, name='editentry'),
]

