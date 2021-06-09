import os
from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.response import Response
from rest_framework import status


class CustomPageNumberPagination(PageNumberPagination):
    """ A custom DRF paginator class
    """
    page_query_param = 'page'

    page_size_query_param = 'limit'
    max_page_size = int(os.getenv('DJANGO_PAGINATION_LIMIT', 100))
