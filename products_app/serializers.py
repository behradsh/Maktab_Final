from rest_framework import serializers
from .models import Category, Product, Comment


class CategorySerializer(serializers.ModelSerializer):
    created_at_shamsi = serializers.SerializerMethodField()
    num_of_products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['created_at_shamsi', 'num_of_products']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def get_num_of_products(self, obj):
        return obj.num_of_products()


class ProductSerializer(serializers.ModelSerializer):
    created_at_shamsi = serializers.SerializerMethodField()
    updated_at_shamsi = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at_shamsi', 'updated_at_shamsi', 'store']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def get_updated_at_shamsi(self, obj):
        return obj.updated_at_shamsi

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    created_at_shamsi = serializers.SerializerMethodField()
    updated_at_shamsi = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'product_name', 'rating', 'description', 'status', 'created_at', 'created_at_shamsi',
                  'updated_at_shamsi']
        read_only_fields = ['created_at_shamsi', 'updated_at_shamsi']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def get_updated_at_shamsi(self, obj):
        return obj.updated_at_shamsi
