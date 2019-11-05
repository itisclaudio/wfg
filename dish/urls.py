from django.conf.urls import patterns, include, url
import settings

from django.conf.urls import handler500, handler404, handler403#, handler400
from dish.files.views import myerror500, myerror404, myerror403#, myerror400

#START-django-ajax-selects app
from django.conf.urls.static import static
#from django.conf import settings
#from ajax_select import urls as ajax_select_urls
#START-django-ajax-selects app

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^',include('dish.files.urls')),
	url(r'^accounts/', include('allauth.urls')),#For:django-allauth

	#url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),

	#url(r'^ajax_select/', include(ajax_select_urls)),#django-ajax-selects
] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)

# This line is for django-ajax-selects:
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#For debug_toolbar (Only Development):
#if settings.DEBUG:
if settings.LOCAL_DEV:
	#print "settings.DEBUG = True, Load debug_toolbar"
	import debug_toolbar
	urlpatterns = [
		url(r'^__debug__/', include(debug_toolbar.urls)),
		url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
	] + urlpatterns
else:
	import os
	urlpatterns = [
	#url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':os.environ.get('MEDIA_URL_AWS')}),
	url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
] + urlpatterns

#To handle Errors
handler500 = myerror500
handler404 = myerror404
handler403 = myerror403
#handler400 = myerror400
#django can't import handler400 so Django is handleing 400 error