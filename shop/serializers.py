from rest_framework import serializers

from shop.models import Product, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name']
