import uuid

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """ Flite Abstract base model.
    This abstract model will contain fields and common method"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True
