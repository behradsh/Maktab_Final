import django_filters.rest_framework as filters
from .models import Product
class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    brand = filters.CharFilter(field_name='brand', lookup_expr='icontains')
    price = filters.CharFilter(field_name='price', lookup_expr='gte')
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name','brand','price','created_at']