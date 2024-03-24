import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient, RecipeTag


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


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = RecipeTag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient', read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
    
    def get_is_favorited(self, obj):
        return True
    
    def get_is_in_shopping_cart(self, obj):
        return True


class RecipeIngredientReadSerializer(RecipeIngredientSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )


class RecipeIngredientWriteSerializer(RecipeIngredientSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

class RecipeReadSerializer(RecipeSerializer):
    tags = RecipeTagSerializer(source='recipe_tag', many=True)
    ingredients = RecipeIngredientReadSerializer(source='recipe_ingredient', many=True)


class RecipeWriteSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)

    def create(self, validated_data: dict):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            amount = ingredient['amount']
            current_ingredient = ingredient['id']
            print(">>>", f"current_ingredient = {current_ingredient}, amount = {amount}")
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount
            )
        for tag in tags:
            print(">>>", f"tag = {tag}")
            RecipeTag.objects.create(tag=tag, recipe=recipe)

        return recipe
    
    def to_representation(self, data):
        return RecipeReadSerializer(context=self.context).to_representation(data)