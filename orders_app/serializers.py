from rest_framework import serializers
from orders_app.models import Orders,OrderItems
from users_app.serializers import AddressSerializer
from products_app.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItems
        fields = ['id', 'product', 'quantity', 'price', 'discount']

class OrderSerializer(serializers.ModelSerializer):
    orderitems_set = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Orders
        fields = ['id', 'status', 'discount', 'total_amount', 'created_at', 'orderitems_set','store','customer']
