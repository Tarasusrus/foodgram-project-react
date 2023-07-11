from django.contrib.auth import get_user_model
from django_filters import rest_framework
from recipes.models import Recipe
from rest_framework.filters import SearchFilter

User = get_user_model()


class NameSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    """
    Фильтры для модели Recipe.

    author - фильтрация по автору рецепта.
    tags - фильтрация по тегам рецепта.
    is_favorited - фильтрация по избранным рецептам текущего пользователя.
    is_in_shopping_cart - фильтрация по рецептам,
    находящимся в корзине покупок текущего пользователя.
    """

    author = rest_framework.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = rest_framework.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрация рецептов по избранным рецептам текущего пользователя.

        queryset - исходный набор данных рецептов.
        name - имя поля фильтра.
        value - значение фильтра.

        Возвращает отфильтрованный набор данных рецептов.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрация рецептов по рецептам,
        находящимся в корзине покупок текущего пользователя.

        queryset - исходный набор данных рецептов.
        name - имя поля фильтра.
        value - значение фильтра.

        Возвращает отфильтрованный набор данных рецептов.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping__user=self.request.user)
        return queryset
