from rest_framework import serializers
from src.config.store_app.models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address','store_city']
        read_only_fields = ['id']
