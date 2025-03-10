from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product."""
    class Meta:
        model = Product
        fields = [
            'pk',
            'name',
            'description',
            'price',
            'discount',
            'created_at',
            'archived',
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order."""
    class Meta:
        model = Order
        fields = [
            'pk',
            'delivery_address',
            'promocode',
            'created_at',
            'user',
            'products',
        ]
