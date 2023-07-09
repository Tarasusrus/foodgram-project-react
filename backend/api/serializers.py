from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Follow, User


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class MyUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Follow.objects.filter(
            user=user, author=obj).exists()


class FollowSerializer(MyUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'recipes_count', 'recipes',
                  'is_subscribed')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeShortSerializer(recipes, many=True,
                                           context=self.context)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        # f


class IngredientInRecipeCreateSerializer(ModelSerializer):

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')

    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeReadSerializer(ModelSerializer):

    tags = TagsSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(
        source='recipeingredients', many=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favourite.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipe=obj).exists()


class RecipeCreateSerializer(ModelSerializer):
    '''Сериализатор создания рецепта'''

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        for i in value:
            if i['amount'] <= 0:
                raise ValidationError('Колличество должно быть больше 0')
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        Recipe_bulk = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'))
            for ingredient in ingredients]

        RecipeIngredients.objects.bulk_create(Recipe_bulk)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient['amount']
                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient.get('id'),
                    defaults={'amount': amount})
        return super().update(instance, validated_data)
