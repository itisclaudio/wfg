from .base import *
# Override base.py settings here
#print "in production.py"

DEBUG = True
ALLOWED_HOSTS = ['wfg-p.herokuapp.com','wfg-s.herokuapp.com','wfg.herokuapp.com/','wfgs.s3.amazonaws.com','www.worldfood.guide','worldfood.guide']
INSTALLED_APPS += (
	'storages',#App needed for Amazon AWS S3
	#'whitenoise.runserver_nostatic',
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY','afl549q&v2eppw3reii)7wozdeyiol47n)hr7^fis*g#5a!-e04=')

MIDDLEWARE_CLASSES = (
	#'whitenoise.middleware.WhiteNoiseMiddleware',
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

#BASE_URL = 'https://wfg-s.herokuapp.com/' # By me: for global_constants
BASE_URL = os.environ.get('BASE_URL') # By me: for global_constants, not harcoding, ex: https://wfg-p.herokuapp.com/

import dj_database_url
#db_from_env = dj_database_url.config()
DATABASES = {
	'default': dj_database_url.config()
}
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'dish/static'),
)
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

#So whitenoise can handle storage in heroku
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# To load different files when run localy, like in url for debug_toolbar
LOCAL_DEV = False

#Heroku variable for https:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#Variable so http redirects to https since Heroku doesn't do this automaticaly
SECURE_SSL_REDIRECT = True

#For Amazon S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-west-2'
#AWS_STORAGE_BUCKET_NAME = "s3-us-west-2"
#AWS_DEFAULT_REGION = 'us-west-2'
#AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False#Doesn't add signature after media files
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#New for Amazon:
#MEDIA_URL = "https://s3-us-west-2.amazonaws.com/wfgs/"
#MEDIA_URL = "https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/"
#MEDIA_URL = "https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/"
MEDIAFILES_LOCATION = 'media'

#### Adding this will tell django to save uploaded files to S3 bucket
#### and use S3 URL to link them
DEFAULT_FILE_STORAGE = 'custom_storages.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'custom_storages.StaticRootS3BotoStorage'
#S3_URL = 'https://wfgs.s3-us-west-2.amazonaws.com/'
S3_URL = 'https://{}.s3-{}.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME)
#S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

# If we're not using our S3 backend storage we need to serve the media files via path
#if DEFAULT_FILE_STORAGE == "custom_storages.MediaRootS3BotoStorage":
#	MEDIA_URL = 'https://%s.s3-us-west-2.amazonaws.com/%s/' % (AWS_STORAGE_BUCKET_NAME, MEDIAFILES_LOCATION)
#else:
#MEDIA_URL = '/media/'

#MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
#MEDIA_URL = 'media'
#MEDIA_ROOT = MEDIA_URL
#MEDIA_ROOT = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = os.path.join(S3_URL, "media")
#MEDIA_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)),'media/'))
#MEDIA_ROOT = 'https://worldfood.guide/media/'
STATIC_URL = S3_URL + 'static/'
MEDIA_URL = S3_URL + 'media/' #Also used in views to check if photo has been uloaded
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

#STATIC_URL = 'https://%s.s3.amazonaws.com/static/' % AWS_STORAGE_BUCKET_NAME
#AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
#MEDIA_URL = '//s3-%s.s3.amazonaws.com/%s/' % (S3DIRECT_REGION,AWS_STORAGE_BUCKET_NAME)
#MEDIA_URL = S3_URL

#MEDIA_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)),'media/'))

#To send emails with sendgrid (Heroku add on)
SEND_GRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'app153913174@heroku.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (('Claudio', 'itisclaudio@gmail.com'),) # A tuple that lists people who get code error notifications. When DEBUG=False