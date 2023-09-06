from rest_framework import serializers

from shop.models import Cart, CartItem, Shelf, Order, OrderItem, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']


class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = ['name']


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

    def create(self, validated_data):
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


class OrderItemSerializer(serializers.ModelSerializer):
    item = ShelfSerializer()

    class Meta:
        model = OrderItem
        fields = ['item']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "region", "order_items", "status"]
        read_only_fields = ['status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    region = serializers.CharField(max_length=200)

    def validate(self, data):
        """
        Validates the cart and order regions match.
        :param attrs: validated data
        """
        if data['region'] != Cart.objects.get(id=data['cart_id']).region.name:
            raise serializers.ValidationError("Cart and order regions don't match.")
        return data

    def validate_cart_id(self, value):
        """
        Checks if the cart belong to user.
        :param value: cart id
        """
        if not Cart.objects.filter(id=value, user=self.context['request'].user).exists():
            raise serializers.ValidationError("Cart does not belong to user or does not exist.")
        return value

    def validate_region(self, value):
        """
        Checks if the region exists.
        :param value: region name
        """
        if not Region.objects.filter(name=value).exists():
            raise serializers.ValidationError("Region does not exist.")
        return value
