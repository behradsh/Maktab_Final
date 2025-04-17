from django.shortcuts import render
from rest_framework.views import APIView

from .models import (Category,Product)
from .serializers import (CategorySerializer,ProductSerializer)
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
# Create your views here.

class CategoryView(APIView):
    """
    Viewset for get all categories
    """
    queryset = Category.objects.all()
    serializer = CategorySerializer(many=True)

class ProductView(APIView):
    category = CategorySerializer()
    serializer = ProductSerializer(many=True)
    queryset = Product.objects.all()
    class Meta:
        model = Product
        fields = '__all__'