from rest_framework import serializers

from carts.models import CartItem, Cart


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["shelf"]


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)

    class Meta:
        model = Cart

        fields = ['id', 'region', 'status', 'cart_items']
        read_only_fields = ['id', 'status']
        extra_kwargs = {
            'region': {'write_only': True},
            'cart_items': {'write_only': True},
        }

    def create(self, validated_data: dict) -> Cart:
        """
        Create or get a cart with cart items.
        :param validated_data: region id and cart items
        :return: Cart
        """
        cart_items = validated_data.pop('cart_items')
        cart, created = Cart.objects.get_or_create(**validated_data)

        for cart_item in cart_items:
            CartItem.objects.create(cart=cart, **cart_item)
        return cart
