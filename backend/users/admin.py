from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""

    list_display = ['username', 'email', 'role', 'full_name', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Links', {
            'fields': ('person',),
            'description': 'Link this user to a Person record if applicable'
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'first_name', 'last_name'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']
