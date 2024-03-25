from api.pagination import CustomPagination
from typing import Any
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import CustomUserSerializer  # , SubscribeSerializer

from .models import Subscribe

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    print(queryset)
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
