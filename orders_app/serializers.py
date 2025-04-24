from rest_framework import serializers
from orders_app.models import Orders, OrderItems,Cart,CartItem
from users_app.models import Address
from store_app.models import Store
from store_app.serializers import StoreSerializer
from users_app.serializers import AddressSerializer
from products_app.serializers import ProductSerializer
from products_app.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    created_at_shamsi = serializers.SerializerMethodField()
    updated_at_shamsi = serializers.SerializerMethodField()
    product = ProductSerializer()

    class Meta:
        model = OrderItems
        fields = ['id', 'product', 'quantity', 'price', 'discount', 'created_at_shamsi', 'updated_at_shamsi']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def get_updated_at_shamsi(self, obj):
        return obj.updated_at_shamsi


class OrderSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source='store', write_only=True
    )
    shipping_address = AddressSerializer(read_only=True)
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), source='shipping_address', write_only=True
    )
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Orders
        fields = ['id', 'store', 'store_id', 'total_amount', 'status', 'created_at', 'shipping_address',
                 'shipping_address_id', 'items','created_at_shamsi', 'updated_at_shamsi']
        read_only_fields = ['total_amount', 'status', 'created_at']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def get_updated_at_shamsi(self, obj):
        return obj.updated_at_shamsi

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']
        read_only_fields = ['subtotal']

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity

    def validate(self, data):
        product = data['product']
        quantity = data.get('quantity', 1)
        if quantity <= 0:
            raise serializers.ValidationError('Quantity must be positive')
        if quantity > product.quantity:
            raise serializers.ValidationError(f'Not Enough Products for {product.name}')
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    created_at_shamsi = serializers.SerializerMethodField()
    updated_at_shamsi = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']
        read_only_fields = ['total']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def get_updated_at_shamsi(self, obj):
        return obj.updated_at_shamsi

    def get_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

