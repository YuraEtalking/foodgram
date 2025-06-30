from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import AvatarUpdateSerializer, CustomUserSerializer
from users.models import Subscription, User
from yaml import serialize


class CustomUserViewSet(DjoserUserViewSet):

    def list(self, request):
        users_list = User.objects.all()
        serializer = CustomUserSerializer(
            users_list,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['delete', 'post'])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
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

    @action(detail=False, methods=['get',])
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [subscription.author for subscription in subscriptions]
        serializer = CustomUserSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['delete', 'patch'], url_path='me/avatar')
    def update_and_delete_avatar(self, request):
        user = request.user
        if request.method == 'PATCH':
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
