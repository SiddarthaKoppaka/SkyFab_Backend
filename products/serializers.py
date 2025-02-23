from rest_framework import serializers
from .models import Product, ProductImage, Category, SubCategory


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_accessory']


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for SubCategory model.
    """
    class Meta:
        model = SubCategory
        fields = ['id', 'name']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model using Google Drive URLs.
    """
    class Meta:
        model = ProductImage
        fields = ['image_url']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model with associated category, subcategory, and images.
    """
    images = ProductImageSerializer(many=True, read_only=True)  # Fetch multiple images
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'serial_number',
            'name',
            'design',
            'sku',
            'product_type',
            'price_with_shipping',
            'sizes',
            'category_name',  # Category name instead of ID
            'subcategory_name',  # SubCategory name instead of ID
            'images',
        ]
