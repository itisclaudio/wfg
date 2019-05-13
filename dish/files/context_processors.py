# Library created to access constants in templates and views
#https://chriskief.com/2013/09/19/access-django-constants-from-settings-py-in-a-template/

from django.conf import settings

def global_constants (request):
	# return any necessary values
	return {
		'BASE_URL': settings.BASE_URL, #By me: For multiple uses like modals
		#'TEST_1': "http://localhost:8000/"
	}