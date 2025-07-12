"""Модуль для админки приложения пользователей."""
from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели User"""
    list_display = (
        'email',
        'username',
        'display_full_name',
        'avatar',
    )
    search_fields = ['email', 'username']

    @admin.display(description='Полное имя')
    def display_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для модели Subscription"""

    list_display = (
        'user',
        'author',
        'created_at',
    )
    search_fields = ['user__username', 'author__username']
