from django.shortcuts import get_object_or_404, render
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeIngredientReadSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer)


class RecipePagination(PageNumberPagination):
    page_size = 2


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    # serializer_class = RecipeReadSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    # permission_classes = ()
    # filter_backends = []