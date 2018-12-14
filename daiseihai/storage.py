import os

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name
