""" Checks for resource existence"""
from rest_framework import status

def resource_exists(model, kwargs):
    """Checks if resource exists."""

    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return False
