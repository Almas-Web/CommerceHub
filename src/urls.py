from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    #path('api/products/', include('products.urls')),
    #path('api/categories/', include('categories.urls')),
    #path('api/cart/', include('cart.urls')),
    #path('api/wishlist/', include('wishlist.urls')),
    #path('api/orders/', include('orders.urls')),
    #path('api/payments/', include('payments.urls')),
    #path('api/reviews/', include('reviews.urls')),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)