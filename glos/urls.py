from django.conf.urls import url
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as authviews
from . import views
from . import viewslocstar
from django.conf.urls import include, url
from django.conf import settings

#handler404 = views.handler404
#app_name = 'glos'
urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
    url(r'^edit/(\d+)/$', views.editentry, name='editentry'),
    #url(r'^upload/', views.upload, name="upload"),
    url(r'^terms/', views.term_list),
    url(r'^user_termbase/', views.user_termbase_list),
    url(r'^language/', views.language_list),
    url(r'^termbase/', views.termbase_list),
    url(r'^create_termbase/', views.termbase_create),
    url(r'^delete_termbase/', views.termbase),
    url(r'^create_term/', views.term_create),
    url(r'^create_term_merge/', views.term_create_merge),
    url(r'^create_language/', views.language_create),
	#url(r'^search/',views.search, name="search"),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
    url(r'^create_post/', views.create_post),
    url(r'^servicegrid/', viewslocstar.servicegrid, name='servicegrid'),
    url(r'^translation/', viewslocstar.translation, name='translation'),
    url(r'^localization/', viewslocstar.localization, name='localization'),
    url(r'^website/', viewslocstar.website, name='website'),
    url(r'^other/', viewslocstar.other, name='other'),
    url(r'^locstar/', viewslocstar.locstar, name='locstar'),
    url(r'^technologie/', viewslocstar.technologie, name='technologie'),
	url(r'^onas/', viewslocstar.onas, name='onas'),
	url(r'^tm/', viewslocstar.tm, name='tm'),
	url(r'^terminology/', viewslocstar.terminology, name='terminology'),
	url(r'^tools/', viewslocstar.tools, name='tools'),
	url(r'^mt/', viewslocstar.mt, name='mt'),
	url(r'^customers/', viewslocstar.customers, name='customers'),
    url(r'^lspsoftware/', views.lspsoftware, name='lspsoftware'),
    url(r'^contact/', viewslocstar.contact, name='contact'),
    url(r'^special/', viewslocstar.special, name='special'),
    url(r'^prices/', viewslocstar.prices, name='prices'),
]

