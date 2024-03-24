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


# class RecipeTagSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ('__all__')
#         model = RecipeTag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # name = serializers.StringRelatedField(source='ingredient', read_only=True)
    # measurement_unit = serializers.StringRelatedField(
    #     source='ingredient.measurement_unit',
    #     read_only=True
    # )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для безопасных методов."""
    
    # def __init__(self, instance=None, data=..., **kwargs):
    #     super().__init__(instance, data, **kwargs)
        # print("DEBUG", self.data)

    tags = TagSerializer(many=True, read_only =True)
    # author = CustomUserSerializer(read_only=True)
    # ingredients = RecipeIngredientSerializer()
    # image = Base64ImageField()
    # is_favorite = serializers.SerializerMethodField(read_only=True)
    # is_in_shopping_cart  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            # 'author',
            # 'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            # 'image',
            'text',
            'cooking_time',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """."""

    # tags = serializers.PrimaryKeyRelatedField()
    # def __init__(self, instance=None, data=..., **kwargs):
    #     super().__init__(instance, data, **kwargs)
        # pprint(self.context)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            # 'author',
            # 'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            # 'image',
            'text',
            'cooking_time',
        )
    
    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data