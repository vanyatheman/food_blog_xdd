from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, RecipeShortSerializator)

from .help_tools.views_tools import add_recipe, delete_recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = Recipe.objects.filter(id=pk)
        exist: bool = Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            return add_recipe(
                Favorite, RecipeShortSerializator, user, recipe, exist
            )

        if request.method == 'DELETE':
            return delete_recipe(Favorite, user, recipe, exist)
        
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        exist: bool = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            return add_recipe(
                ShoppingCart, RecipeShortSerializator, user, recipe, exist
            )

        if request.method == 'DELETE':
            return delete_recipe(ShoppingCart, user, recipe, exist)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """."""

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
