from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    AvatarUpdateSerializer,
    CustomUserSerializer,
    SubscriptionsSerializer
)
from recipes.pagination import LimitPageNumberPagination
from users.models import Subscription


User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    pagination_class = LimitPageNumberPagination

    def list(self, request):
        users_list = User.objects.all()
        page = self.paginate_queryset(users_list)
        serializer = CustomUserSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Пользователь не авторизован.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['delete', 'post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author
            )
            if created:
                serializer = CustomUserSerializer(
                    author,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Уже подписался'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=request.user,
                author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Не подписан'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [subscription.author for subscription in subscriptions]

        paginator = LimitPageNumberPagination()

        page = paginator.paginate_queryset(authors, request)

        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['delete', 'put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def update_and_delete_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarUpdateSerializer(
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.update(user, serializer.validated_data)
                user.save()
                avatar = self.get_serializer(
                    user,
                    context={'request': request}
                ).data['avatar']
                return Response(
                    {'avatar': avatar},
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
