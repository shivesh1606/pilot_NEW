from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_createdby', null=True, blank=True, on_delete = models.SET_NULL)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_modifiedby', null=True, blank=True, on_delete = models.SET_NULL)

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     if kwargs.get("user") is not None:
            