from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.views import RecipeViewSet, IngredientViewSet, TagViewSet

app_name = "api"

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls))
]
