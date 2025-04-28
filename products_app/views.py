from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework import generics,permissions
from .models import (Category,Product,Comment)
from .serializers import (CategorySerializer,ProductSerializer,CommentSerializer)
from core_app.custom_permissions import *
from store_app.models import Store
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
# Create your views here.


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated,IsCustomer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated,IsCustomer]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

class CustomerCommentsListTemplate(TemplateView):
    template_name = "dashboards/customer_dashboard_comments.html"

class SellerProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]

    def get_queryset(self):
        store = Store.objects.get(owner=self.request.user)
        return Product.objects.filter(store=store).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        if user.groups.filter(name='SellerOperators').exists():
            raise Exception("Operators cannot create products.")
        store = Store.objects.get(owner=self.request.user)
        serializer.save(store=store)

class SellerProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]

    def get_queryset(self):
        store = Store.objects.get(owner=self.request.user)
        return Product.objects.filter(store=store)

    def perform_update(self, serializer):
        user = self.request.user
        if user.groups.filter(name='SellerOperators').exists():
            raise Exception("Operators cannot update products.")
        serializer.save()


    def perform_destroy(self, instance):
        user = self.request.user
        if user.groups.filter(name='SellerOperators').exists():
            raise Exception("Operators cannot delete products.")
        instance.delete()



class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]

class ProductListHomeView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class CategoryListHomeView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class SellerDashboardCreateProductTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_products_add.html"

class SellerDashboardListProductTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_products.html"

class SellerDashboardEditProductTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_products_edit.html"

class SellerCategoryListTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_category.html"
class SellerCategoryUpdateTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_category_edit.html"
class SellerCategoryCreateTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_category_add.html"