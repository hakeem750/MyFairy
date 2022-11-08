from rest_framework import serializers
from product.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "title", "subtitle", "price", "images", "slug")


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "subtitle",
            "description",
            "price",
            "images",
            "average_rating",
            "discount",
        )
