from django.contrib import admin

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    '''Админка Тегов.'''
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''Админка ингредеентов'''

    list_display = ('pk', 'name', 'author', 'text',
                    'cooking_time', 'image', 'date')
    search_fields = ('name', 'author', 'text', 'cooking_time')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('favarite_count',)
    inlines = (RecipeIngredientsInLine,)

    def favarite_count(self, obj):
        '''Количество избранных.'''
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''Админка иингредентов.'''
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')


@admin.register(RecipeIngredients)
class RecipeIngridientsAdmin(admin.ModelAdmin):
    '''Админка ингредентов в рецептах.'''

    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    '''Админка покупок.'''

    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    '''Админка избранноого'''

    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
