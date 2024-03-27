from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart, RecipeIngredient
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, RecipeShortSerializator)

from .help_tools.views_tools import add_recipe, delete_recipe, get_user_recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorAdminOrReadOnly,)
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
        user, recipe, exist = get_user_recipe(request, pk, Favorite)
        print(">>> DEBUG", user, recipe, exist, sep='\n')

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
        user, recipe, exist = get_user_recipe(request, pk, ShoppingCart)

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
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f"Список покупок для: {user.get_full_name()}\n"
            f"Дата: {today:%Y-%m-%d}\n\n"
        )
        shopping_list += '\n'.join([
            f"- {ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']})"
            f" - {ingredient['amount']}"
            for ingredient in ingredients
        ])

        filename = f"Shopping_list-_-{today}.txt"
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f"attachment; filename={filename}"

        return response

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
