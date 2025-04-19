from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics,permissions
from .models import (Category,Product,Comment)
from .serializers import (CategorySerializer,ProductSerializer,CommentSerializer)
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

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

