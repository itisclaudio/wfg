from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

#MediaRootS3BotoStorage  = lambda: S3Boto3Storage(location='media')
class MediaRootS3BotoStorage(S3Boto3Storage):
	location = settings.MEDIAFILES_LOCATION