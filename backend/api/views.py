from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.filters import NameSearchFilter, RecipeFilter
from api.pagination import CustumPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FollowSerializer, IngredientSerializer,
                             MyUserSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, RecipeShortSerializer,
                             TagsSerializer)
from api.utils import download_cart
from recipes.models import Favourite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User


class MeUserViewSet(UserViewSet):
    """
    Представление для работы с пользователями и их подписками.

    Представление позволяет получать список пользователей и
    информацию о подписках,
    а также подписываться на других пользователей или отписываться от них.

    Атрибуты:
    - queryset: queryset объектов пользователей
    - serializer_class: класс сериализатора пользователей
    - pagination_class: класс пагинации

    Методы:
    - subscriptions: метод для получения списка подписок пользователя
    - subscribe: метод для подписки на пользователя или отписки от него
    """

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = CustumPagination

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """
        Получение списка подписок пользователя.

        Метод позволяет получить список пользователей,
        на которых подписан текущий
        пользователь.

        Аргументы:
        - request: объект запроса

        Возвращает:
        Ответ с данными о подписках пользователя.

        Права доступа:
        - Только аутентифицированные могут использовать данный метод.
        """
        user = request.user
        queryset = User.objects.filter(followers__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """
        Подписка на пользователя или отписка от него.

        Метод позволяет подписаться на пользователя или
        отписаться от него.

        Аргументы:
        - request: объект запроса
        - id: идентификатор пользователя

        Возвращает:
        Ответ с данными о пользователе,
        на которого произведена подписка или отписка.

        Права доступа:
        - Только аутентифицированные могут использовать данный метод.
        """
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {'detail': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(author=author, user=user).exists():
                return Response(
                    {'detail': 'Вы уже подписаны!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы не подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = get_object_or_404(Follow, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Представление для работы с тегами.

    Представление позволяет получать список тегов и информацию о каждом теге.

    Атрибуты:
    - queryset: queryset объектов тегов
    - serializer_class: класс сериализатора тегов
    - permission_classes: классы разрешений
    - pagination_class: класс пагинации
    """

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Представление для работы с ингредиентами.

    Представление позволяет получать список ингредиентов и
    информацию о каждом ингредиенте.

    Атрибуты:
    - queryset: queryset объектов ингредиентов
    - serializer_class: класс сериализатора ингредиентов
    - permission_classes: классы разрешений
    - filter_backends: классы фильтрации
    - search_fields: поля для поиска
    - pagination_class: класс пагинации
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (NameSearchFilter,)
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с рецептами.

    Представление позволяет создавать, получать, обновлять и удалять рецепты,
    а также добавлять рецепты в избранное и список покупок.

    Атрибуты:
    - queryset: queryset объектов рецептов
    - permission_classes: классы разрешений
    - pagination_class: класс пагинации
    - filter_backends: классы фильтрации
    - filterset_class: класс фильтра
    - http_method_names: поддерживаемые методы HTTP

    Методы:
    - get_serializer_class: метод для выбора класса сериализатора в зависимости
     от метода запроса
    - perform_create: метод для выполнения действий при создании рецепта
    - perform_update: метод для выполнения действий при обновлении рецепта
    - favorite: метод для добавления или удаления рецепта в избранное
    - shopping_cart: метод для добавления или удаления рецепта в список покупок
    - download_shopping_cart: метод для скачивания списка покупок
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustumPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post',
                 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        Добавление или удаление рецепта в избранное.

        Метод позволяет добавлять или удалять рецепты в
        избранное для текущего пользователя.

        Аргументы:
        - request: объект запроса
        - pk: идентификатор рецепта

        Возвращает:
        Ответ с данными о рецепте, добавленном или удаленном из избранного.

        Права доступа:
        - Только аутентифицированные могут использовать данный метод.
        """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favourite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = get_object_or_404(Favourite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """
        Добавление или удаление рецепта в список покупок.

        Метод позволяет добавлять или удалять рецепты в
        список покупок для текущего пользователя.

        Аргументы:
        - request: объект запроса
        - pk: идентификатор рецепта

        Возвращает:
        Ответ с данными о рецепте, добавленном или удаленном из списка покупок.

        Права доступа:
        - Только аутентифицированные могут использовать данный метод.
        """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Уже в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not user.shopping_cart.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_cart = get_object_or_404(
                ShoppingCart, user=user,
                recipe=recipe
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """
        Скачивание списка покупок.

        Метод позволяет скачать список покупок в виде текстового файла.

        Аргументы:
        - request: объект запроса

        Возвращает:
        Ответ с текстовым файлом списка покупок для скачивания.

        Права доступа:
        - Только аутентифицированные пользователи
        могут использовать данный метод.
        """
        return download_cart(request)
