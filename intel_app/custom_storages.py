from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False

# from django.core.files.storage import FileSystemStorage
#
#
# class MediaStorage(FileSystemStorage):
#     # Optionally, you can override location if needed,
#     # otherwise FileSystemStorage defaults to MEDIA_ROOT.
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('location', settings.MEDIA_ROOT)
#         super().__init__(*args, **kwargs)
