from rest_framework import serializers

from apps.store.models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title', 'description', 'image']
        read_only_fields = ['id', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'slug', 'title', 'description', 'category', 'price', 'available_quantity']
        read_only_fields = ['id', 'slug']


class ProductImage(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']
        read_only_fields = ['id', 'slug']
