from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart
from custom_users.models import Subscribe
from .help_tools.serializers_tools import add_ingredients, Base64ImageField


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (CustomUserSerializer.Meta.fields
        + ('recipes', 'recipes_count')) 
        read_only_fields = ('email', 'username', 'last_name', 'first_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeShortSerializator(recipes, many=True, read_only=True)
        return serializer.data
    
    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise ValidationError(
                detail='Нельзя подписываться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        subscribtion_exist = Subscribe.objects.filter(
            author=author, user=user
        ).exists()
        if subscribtion_exist:
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.StringRelatedField(
        source="ingredient.name",
        read_only=True,
    )
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount"
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredient.objects.all()
    # )
    id = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для безопасных методов."""

    tags = TagSerializer(many=True, read_only =True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source="recipe_ingredients",
    )
    # image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            # 'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        queryest = Favorite.objects.filter(user=user, recipe=obj)
        return queryest.exists()
    
    def get_is_in_shopping_cart(self, obj):
        """."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        queryest = ShoppingCart.objects.filter(user=user, recipe=obj)
        return queryest.exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'image',
            'name',
            'text',
            'cooking_time',
        )
    
    def create(self, validated_data: dict):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data: dict):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        add_ingredients(ingredients, instance)
        instance.save()
        return instance

    def validate(self, data):
        if not self.initial_data.get("ingredients"):
            raise ValidationError("Рецепт не может быть без ингредиентов.")
        if not self.initial_data.get("tags"):
            raise ValidationError("Рецепт не может быть без тега.")
        return data

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item["id"])
            except Ingredient.DoesNotExist:
                raise ValidationError("Указан несуществующий ингредиент.")

            if ingredient in ingredients_list:
                raise ValidationError("Ингредиенты должны быть уникальными.")

            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError("Теги должны быть уникальными.")
        return tags

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data
    

class RecipeShortSerializator(serializers.ModelSerializer):
    """Для ответа на пост запросы на url избранного и корзины."""
    
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            # 'image',
            'cooking_time',
        )
