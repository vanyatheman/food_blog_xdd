from api.pagination import CustomPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import CustomUserSerializer, SubscribeSerializer

from .models import Subscribe

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(detail=False)
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        
        return self.get_paginated_response(serializer.data)
    
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author =  get_object_or_404(User, id=id)
        exist: bool = Subscribe.objects.filter(
            user=user,
            author=author
        ).exists()
        if request.method == 'POST':
            if exist:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                author,
                data = request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            if exist:
                subscribtion = Subscribe.objects.get(user=user, author=author)
                subscribtion.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    

        