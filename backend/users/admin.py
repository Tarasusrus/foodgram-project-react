from django.contrib import admin

# Register your models here. #  api_yamdb
from users.models import Follow, User


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    """Пользователь."""

    list_display = ('username', 'email', 'first_name',
                    'last_name', 'password',)

    search_fields = ('username', 'email',)

    list_filter = ('username', 'email',)


@admin.register(Follow)
class FolowAdmin(admin.ModelAdmin):
    """Подписчик."""

    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
