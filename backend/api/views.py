from django.shortcuts import get_object_or_404, render
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart

from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, RecipeShortSerializator)


class RecipePagination(PageNumberPagination):
    page_size = 2


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    # serializer_class = RecipeReadSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer
    
    def perform_create(self, serializer):
        print(">>> Views DBUG ", self.request.user)
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        exist: bool = Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if exist:
                return Response(
                    {'errors': "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializator(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if exist:
                favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нет рецепта'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        exist: bool = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if exist:
                return Response(
                    {'errors': "Рецепт уже в корзине."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializator(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if exist:
                cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нет рецепта'},
                status=status.HTTP_400_BAD_REQUEST
            )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    # permission_classes = ()
    # filter_backends = []
