#from prosoft.settings.base import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

#TEMPLATE_DEBUG = DEBUG #For error handling
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
	'django.contrib.sites',#For:django-allauth
	'allauth.account',#For:django-allauth
	'allauth.socialaccount',#For:django-allauth
	'allauth.socialaccount.providers.facebook',#For:django-allauth
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'dish.files',
	'crispy_forms',
	'django_mobile',
	'django.contrib.sitemaps',
	'inflection',
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.BrokenLinkEmailsMiddleware', #To send 404 'page not found' error to ADMINS
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django_mobile.middleware.MobileDetectionMiddleware',
	'django_mobile.cache.middleware.CacheFlavourMiddleware',
	'django.middleware.cache.FetchFromCacheMiddleware',
	'django_mobile.middleware.SetFlavourMiddleware',
)

ROOT_URLCONF = 'dish.urls'

WSGI_APPLICATION = 'dish.wsgi.application'

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'wfg_db',
		'USER': 'postgres',
		'PASSWORD': 'claudio',#admin?
	}
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(os.path.dirname(os.path.dirname(__file__)),'templates/')],
		#'DIRS': [os.path.join(PROJECT_ROOT,'templates')],
		#'DIRS': [],
		#'APP_DIRS': True,
        #'APP_DIRS': False, #Because django_mobile
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',#Also for:django-allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_mobile.context_processors.flavour',
				'dish.files.context_processors.global_constants',# By me: for global_constants
            ],
            'loaders':[
				('django_mobile.loader.CachedLoader', [
					'django_mobile.loader.Loader',
					'django.template.loaders.filesystem.Loader',
					'django.template.loaders.app_directories.Loader',
					]),
			],
        },
    }]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False#It was true but to avoid naive datetime using time zone I changed to false


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'dish/static'),
)

UPLOAD_DISH = 'dish/media/dishes'
UPLOAD_USER = 'dish/media/users'

#STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

FLAVOURS = ('full', 'mobile')#mobile middleware
SITE_ID = 1#For:django-allauth


##Start for:django-allauth
LOGIN_REDIRECT_URL = '/myprofile/'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = False

ACCOUNT_EMAIL_VERIFICATION ='optional' #A e-mail verification mail will be sent.
# Required by django-allauth to extend the sign up form to include profile data
ACCOUNT_SIGNUP_FORM_CLASS = 'dish.files.forms.SignupAllauthForm'
#AUTHENTICATION_BACKENDS -> For:django-allauth
AUTHENTICATION_BACKENDS = (
	# Needed to login by username in Django admin, regardless of `allauth`
	'django.contrib.auth.backends.ModelBackend',#For:django-allauth
	# `allauth` specific authentication methods, such as login by e-mail
	'allauth.account.auth_backends.AuthenticationBackend',#For:django-allauth
)
#Alows to set social account providers scope
SOCIALACCOUNT_PROVIDERS = \
	{'facebook':
		 {'METHOD': 'oauth2',
		 'SCOPE': ['email','public_profile', 'user_friends'],
		 'AUTH_PARAMS': {'access_type': 'online'},
		 'FIELDS': ['id',
		    'email',
			'name',
			'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
		  'EXCHANGE_TOKEN': True,
		  'LOCALE_FUNC': lambda request: 'kr_KR',
		  'VERIFIED_EMAIL': False,
		  'VERSION': 'v2.4'
		  },
}
##End for:django-allauth