import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import RecipeIngredient, Ingredient


class Base64ImageField(serializers.ImageField):
    """Декодирование изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


def add_ingredients(ingredients, recipe):
    """Добавить ингредиенты."""

    ingredients_query_list = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(id=ingredient.get("id")),
            amount=ingredient.get("amount"),
        )
        for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(ingredients_query_list)