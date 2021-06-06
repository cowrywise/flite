from rest_framework import status, pagination
from rest_framework.response import Response
from django.conf import settings


class CustomPagination(pagination.PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE')
    page_size_query_param = 'limit'
    max_page_size = 50
    page_query_param = 'page'

    def get_paginated_response(self, data):
        response = dict(results=data)
        response['count'] = self.page.paginator.count
        response['next'] = self.get_next_link()
        response['previous'] = self.get_previous_link()
        return Response(response, status=status.HTTP_200_OK)
