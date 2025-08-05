from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ProductPagination(PageNumberPagination):
    page_size = 18

    def get_paginated_response(self, data):
        return Response({
            'count_item': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })