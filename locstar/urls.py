from django.conf.urls import url
#from . import views
from locstar import views as viewslocstar
from django.conf.urls import include, url
from django.conf.urls import handler404, handler500

#handler404 = viewslocstar.error_404
#handler404 = 'glossary.views.my_custom_page_not_found_view'

#app_name = 'glos'
urlpatterns = [
   
    #url(r'^$', views.index, name='index'),
    #url(r'^locstar/', viewslocstar.locstar, name='locstar'),
    url(r'^$', viewslocstar.locstar, name='locstar'),
    #url(r'^onas/', viewslocstar.error_404, name='onas'),
    url(r'^onas/', viewslocstar.onas, name='onas'),
    url(r'^servicegrid/', viewslocstar.servicegrid, name='servicegrid'),
    url(r'^translation/', viewslocstar.translation, name='translation'),
    url(r'^localization/', viewslocstar.localization, name='localization'),
    url(r'^website/', viewslocstar.website, name='website'),
    url(r'^other/', viewslocstar.other, name='other'),
    url(r'^technologie/', viewslocstar.technologie, name='technologie'),
	url(r'^tm/', viewslocstar.tm, name='tm'),
	url(r'^terminology/', viewslocstar.terminology, name='terminology'),
	url(r'^tools/', viewslocstar.tools, name='tools'),
	url(r'^mt/', viewslocstar.mt, name='mt'),
	url(r'^customers/', viewslocstar.customers, name='customers'),
    url(r'^contact/', viewslocstar.contact, name='contact'),
    url(r'^special/', viewslocstar.special, name='special'),
    url(r'^prices/', viewslocstar.prices, name='prices'),
    url(r'^people/', viewslocstar.people, name='people'),
    url(r'^facebook/', viewslocstar.facebook, name='facebook'),
    url(r'^twitter/', viewslocstar.twitter, name='twitter'),
    url(r'^linkedin/', viewslocstar.linkedin, name='linkedin'),
]

