from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    AvatarUpdateSerializer,
    UserDetailSerializer,
    SubscriptionsSerializer
)
from api.pagination import LimitPageNumberPagination
from users.models import Subscription


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return User.objects.all()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.user == author:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            author=author
        )
        if created:
            serializer = UserDetailSerializer(
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

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        deleted_count, _ = subscription.delete()
        if deleted_count:
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
        subscriptions = User.objects.filter(
             subscribers__user=request.user
         )

        paginator = LimitPageNumberPagination()
        page = paginator.paginate_queryset(subscriptions, request)

        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarUpdateSerializer(
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
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

    @update_avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
