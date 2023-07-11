from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, Recipe,
                                    RecipeIngredients, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from users.models import Follow, User


class TagsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.

    Сериализатор, используемый для преобразования Tag в JSON-представление
    и обратно при выполнении операций сериализации и десериализации.
    """

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class MyUserSerializer(UserSerializer):
    """
    Сериализатор для модели User с дополнительным полем is_subscribed.

    Сериализатор, используемый для преобразования User в JSON-представление
    и обратно при выполнении операций сериализации и десериализации. Добавляет
    дополнительное поле is_subscribed, которое указывает, подписан ли текущий
    пользователь на данного пользователя.
    """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed")

    def get_is_subscribed(self, obj):
        """
        Получает значение поля is_subscribed для данного пользователя.

        Возвращает True, если текущий пользователь аутентифицирован и
        подписан на данного пользователя, иначе возвращает False.

        Args:
            obj: Объект пользователя, для которого проверяется подписка.

        Returns:
            bool: Значение поля is_subscribed для данного пользователя.
        """
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=obj).exists()
        )


class FollowSerializer(MyUserSerializer):
    """
    Сериализатор для модели Follow с дополнительными recipes и recipes_count.

    Сериализатор, используемый для преобразования Follow в JSON-представление
    и обратно при выполнении сериализации и десериализации. Наследуется от
    сериализатора MyUserSerializer и добавляет recipes и recipes_count,
    которые представляют информацию о рецептах, связанных с данной подпиской.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True
    )
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "recipes_count",
            "recipes",
            "is_subscribed",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_recipes(self, obj):
        """
        Получает список рецептов, связанных с данной подпиской.

        Возвращает список рецептов, связанных с автором подписки (obj.author),
        в виде сериализованных данных с использованием RecipeShortSerializer.

        Args:
            obj: Объект подписки, для которой получаются рецепты.

        Returns:
            list: Список сериализованных данных рецептов.
        """
        recipes = obj.author.recipes.all()
        serializer = RecipeShortSerializer(
            recipes, many=True, context=self.context
        )
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.

    Сериализатор, используемый для преобразования Ingredient в JSON
    и обратно при выполнении операций сериализации и десериализации.

    Attributes:
        model: Модель Ingredient, с которой работает сериализатор.
        fields: Поля модели, которые будут сериализованы.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeShortSerializer(ModelSerializer):
    """
    Сериализатор для краткого представления модели Recipe.

    Сериализатор, используемый для преобразования краткого представления Recipe
    в JSON и обратно при выполнении сериализации и десериализации.

    Attributes:
        model: Модель Recipe, с которой работает сериализатор.
        fields: Поля модели, которые будут сериализованы.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class IngredientInRecipeCreateSerializer(ModelSerializer):
    """
    Сериализатор для создания ингредиента в рецепте.

    Сериализатор, используемый для преобразования ингредиента в рецепте
    в JSON-представление и обратно при выполнении операций сериализации и
    десериализации.

    Attributes:
        model: Модель RecipeIngredients, с которой работает сериализатор.
        fields: Поля модели, которые будут сериализованы.
    """

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")

    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount", "name", "measurement_unit")


class RecipeReadSerializer(ModelSerializer):
    """
    Сериализатор для чтения рецепта.

    Сериализатор, используемый для преобразования рецепта в JSON-представление
    при операциях чтения.

    Attributes:
        tags: Сериализатор TagsSerializer для сериализации связанных тегов.
        author: Сериализатор MyUserSerializer для сериализации автора.
        ingredients:
        Сериализатор IngredientInRecipeCreateSerializer для сериализации
            связанных ингредиентов в рецепте.
        image: Поле Base64ImageField для сериализации изображения рецепта.
        is_favorited: Поле SerializerMethodField для определения,
            является ли рецепт избранным для текущего пользователя.
        is_in_shopping_cart: Поле SerializerMethodField для определения,
            находится ли рецепт в списке покупок текущего пользователя.

        Meta:
            model: Модель Recipe, с которой работает сериализатор.
            fields: Поля модели, которые будут сериализованы.
    """

    tags = TagsSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(
        source="recipeingredients", many=True
    )
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Favourite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )


class RecipeCreateSerializer(ModelSerializer):
    """
    Сериализатор для создания рецепта.

    Сериализатор, используемый для преобразования данных рецепта при операции
    создания.

    Attributes:
        tags: Поле PrimaryKeyRelatedField для сериализации связанных тегов.
        author: Сериализатор MyUserSerializer для сериализации автора.
        ingredients: Сериализатор IngredientInRecipeCreateSerializer для
            сериализации связанных ингредиентов в рецепте.
        image: Поле Base64ImageField для сериализации изображения рецепта.

        Meta:
            model: Модель Recipe, с которой работает сериализатор.
            fields: Поля модели, которые будут сериализованы.

    Methods:
        validate_ingredients: Метод для проверки валидности ингредиентов
            в рецепте.
        to_representation:
        Метод для преобразования данных рецепта в JSON-представление.
        create: Метод для создания нового рецепта.
        update: Метод для обновления существующего рецепта.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        """
        Проверяет валидность ингредиентов в рецепте.

        Args:
            value (list): Список ингредиентов в рецепте.

        Raises:
            ValidationError: Если количество ингредиента меньше или равно 0.

        Returns:
            list: Список валидных ингредиентов.
        """
        for i in value:
            if i["amount"] <= 0:
                raise ValidationError("Количество должно быть больше 0")
        return value

    def to_representation(self, instance):
        """
        Преобразует данные рецепта в JSON-представление.

        Args:
            instance (Recipe): Экземпляр модели Recipe.

        Returns:
            dict: JSON-представление данных рецепта.
        """
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(instance, context=context).data

    def create(self, validated_data):
        """
        Создает новый рецепт.

        Args:
            validated_data (dict): Валидированные данные рецепта.

        Returns:
            Recipe: Созданный экземпляр модели Recipe.
        """
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        Recipe_bulk = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )
            for ingredient in ingredients
        ]

        RecipeIngredients.objects.bulk_create(Recipe_bulk)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.

        Args:
            instance (Recipe): Существующий экземпляр модели Recipe.
            validated_data (dict): Валидированные данные рецепта.

        Returns:
            Recipe: Обновленный экземпляр модели Recipe.
        """
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient["amount"]
                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient.get("id"),
                    defaults={"amount": amount},
                )
        return super().update(instance, validated_data)
