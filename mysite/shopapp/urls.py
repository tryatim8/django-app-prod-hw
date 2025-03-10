from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    ProductDetailsView,
    ProductsListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductsDataExportView,
    ProductViewSet,
    LatestProductFeed,
    OrdersListView,
    OrderDetailView,
    OrderViewSet,
    UserOrdersListView,
    UserOrdersExportView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register('product', ProductViewSet)
routers.register('order', OrderViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path('api/', include(routers.urls)),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path('products/latest/feed/', LatestProductFeed(), name='latest_products_feed'),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', UserOrdersExportView.as_view(), name='user_orders_export')
]
