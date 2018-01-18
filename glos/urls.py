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
    url(r'^terms/', views.term_list),
    url(r'^user_termbase/', views.user_termbase_list),
    url(r'^language/', views.language_list),
    url(r'^termbase/', views.termbase_list),
    url(r'^create_termbase/', views.termbase_create),
    url(r'^dtype_update/', views.dtype_update),
    url(r'^delete_termbase/', views.termbase),
    url(r'^create_term/', views.term_create),
    url(r'^create_term_merge/', views.term_create_merge),
    url(r'^create_language/', views.language_create),
]

