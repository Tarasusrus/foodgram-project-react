from rest_framework.pagination import PageNumberPagination


class CustumPagination(PageNumberPagination):
    """
    Пользовательская пагинация.

    page_size_query_param - параметр запроса для указания количества элементов на странице.
    """

    page_size_query_param = 'limit'
