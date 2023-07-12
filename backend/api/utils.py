"""
Модуль, содержащий представление для скачивания списка покупок.

Модуль определяет представление 'download_cart', которое отвечает на запрос
скачивания списка покупок в виде текстового файла.

Функция 'download_cart' выполняет следующие действия:
- Получает список ингредиентов из модели 'RecipeIngredients',
связанных с рецептами,
  находящимися в списке покупок пользователя,
   сгруппированных по названию ингредиента
  и единице измерения.
- Формирует текстовое представление списка покупок,
включая название ингредиента,
  единицу измерения и общее количество.
- Возвращает HTTP-ответ с текстом списка покупок в формате 'text/plain',
с заданными  заголовками и именем файла.

"""
from django.db.models.aggregates import Sum
from django.http import HttpResponse

from api.serializers import RecipeIngredients


def download_cart(request):
    ingredients = (
        RecipeIngredients.objects.filter(recipe__shopping__user=request.user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(amount=Sum("amount"))
    )

    text = ""
    for ingredient in ingredients:
        text += (
            f'•  {ingredient["ingredient__name"]}'
            f'({ingredient["ingredient__measurement_unit"]})'
            f'— {ingredient["amount"]}\n'
        )
    headers = {"Content-Disposition": "attachment; filename=shopping_cart.txt"}
    return HttpResponse(
        text,
        content_type="text/plain; charset=UTF-8",
        headers=headers)
