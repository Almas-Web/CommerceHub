from django.contrib import admin
from .models import CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'is_verified',
        'is_staff',
        'is_active',
    )

    list_filter = (
        'role',
        'is_verified',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'username',
        'email',
    )

    ordering = ('-date_joined',)