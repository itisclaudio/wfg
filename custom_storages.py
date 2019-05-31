from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

StaticRootS3BotoStorage = lambda: S3Boto3Storage(location='static') #'static' is the name of your folder in your bucket
#MediaRootS3BotoStorage = lambda: S3Boto3Storage(location='media')

class MediaRootS3BotoStorage(S3Boto3Storage):
	location = 'media'