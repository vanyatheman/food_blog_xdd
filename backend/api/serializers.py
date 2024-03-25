import base64
from pprint import pprint

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        print(">>> DEBUG in create user serializers")
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )

    # def to_representation(self, instance):
    #     serializer = CustomUserSerializer(instance)
    #     return serializer.data


class CustomUserSerializer(UserSerializer):
    """."""

    # def __init__(self, instance=None, data=..., **kwargs):
    #     print(">>> DEBUG in users serializers")
    #     super().__init__(instance, data, **kwargs)

    # is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        print(">>> asd")
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
        )

    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return Subscribe.objects.filter(user=user, author=obj).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
        source="ingredient",
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

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
    # is_favorite = serializers.SerializerMethodField(read_only=True)
    # image = Base64ImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = CustomUserSerializer(read_only=True)

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
        for ingredient in ingredients:
            amount = ingredient['amount']
            current_ingredient = ingredient['id']
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    # def update(self, validated_data: dict):
    #     """."""

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
