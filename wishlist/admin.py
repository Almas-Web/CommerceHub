from django.contrib import admin
from .models import Wishlist
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('products',)
    readonly_fields = ('created_at',)