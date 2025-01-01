from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializers import ProductImageSerializer

class ProductInCartSerializer(serializers.ModelSerializer):
    primary_image = ProductImageSerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "selling_price",
            "original_price",
            "primary_image",
            "discount_percentage",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "total_price"]
