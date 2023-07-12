"""
URL-маршруты API приложения.

Модуль определяет URL-маршруты для обработки запросов к API.
Используется 'DefaultRouter' из модуля 'rest_framework.routers'
для автоматической
регистрации URL-маршрутов на основе предоставленных представлений.

URL-маршруты включают следующие конечные точки:
- 'users': Регистрация, просмотр, обновление и удаление пользователей.
- 'tags': Просмотр, создание, обновление и удаление тегов.
- 'ingredients': Просмотр, создание, обновление и удаление ингредиентов.
- 'recipes': Просмотр, создание, обновление и удаление рецептов.

URL-маршруты также включают конечную точку 'auth' для обработки аутентификации,
которая использует URL-маршруты из пакета 'djoser.urls.authtoken'.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, MeUserViewSet, RecipeViewSet,
                       TagViewSet)

router = DefaultRouter()
app_name = 'api'

router.register('users', MeUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
