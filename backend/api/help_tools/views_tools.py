from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.db.models import Model
from recipes.models import Recipe
from custom_users.models import User


def get_user_recipe(request, pk, model: Model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)
    exist: bool = model.objects.filter(
        user=user,
        recipe=recipe
    ).exists()

    return user, recipe, exist


def add_recipe(
    model: Model,
    serializator: ModelSerializer,
    user: User,
    recipe: Recipe,
    exist: bool
):
    """Функция для добавления рецепта в избранное или в корзину для покупок"""

    if exist:
        return Response(
            {'errors': "Рецепт уже добавлен."},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(user=user, recipe=recipe)
    serializer = serializator(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_recipe(
    model: Model,
    user: User,
    recipe: Recipe,
    exist: bool
):
    """Функция для удаления рецепта из избранных или из корзины для покупок"""

    if exist:
        object = model.objects.get(user=user, recipe=recipe)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Рецепт не найден.'},
        status=status.HTTP_400_BAD_REQUEST
    )

