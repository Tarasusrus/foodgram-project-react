from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Проверка разрешений: только автор или только чтение.

    - Для методов HTTP, относящихся к безопасным методам (GET, HEAD, OPTIONS),
    разрешается доступ всем.
    - Для методов HTTP, отличных от безопасных методов,
    разрешается доступ только авторизованным пользователям.

    has_object_permission - проверка разрешения для конкретного объекта.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Проверка разрешений: только администратор или только чтение.

    - Для методов HTTP, относящихся к безопасным методам
    (GET, HEAD, OPTIONS), разрешается доступ всем.
    - Для методов HTTP, отличных от безопасных методов,
     разрешается доступ только администраторам.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)
