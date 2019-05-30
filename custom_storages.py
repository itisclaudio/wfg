from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

MediaRootS3BotoStorage  = lambda: S3Boto3Storage(location='media')
StaticRootS3BotoStorage  = lambda: S3Boto3Storage(location='static')
#class MediaRootS3BotoStorage(S3Boto3Storage):
#	location = settings.MEDIAFILES_LOCATION