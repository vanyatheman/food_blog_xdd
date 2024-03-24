import base64
from pprint import pprint

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from django.core.files.base import ContentFile
from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient


class CustomUserSerializer(UserSerializer):
    """."""


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
    # author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source="recipe_ingredients",
    )
    # image = Base64ImageField()
    # is_favorite = serializers.SerializerMethodField(read_only=True)
    # is_in_shopping_cart  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            # 'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            # 'image',
            'text',
            'cooking_time',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            # 'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            # 'image',
            'text',
            'cooking_time',
        )
    
    def create(self, validated_data: dict):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        # print(">>> ", validated_data, ingredients)
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            amount = ingredient['amount']
            current_ingredient = ingredient['id']
            # print(">>> ", f"current_ingredient = {current_ingredient}, amount = {amount}")
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data