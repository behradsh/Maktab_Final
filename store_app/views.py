from django.shortcuts import render
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from core_app.custom_permissions import *
from users_app.models import CustomUser
from .serializers import StoreSerializer,StoreEmployeeCreateSerializer
from rest_framework import (generics, status, views, permissions, viewsets,serializers)
from rest_framework.response import Response
from .models import Store,StoreEmployee
# Create your views here.


class SellerStoreRetrieveView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]
    serializer_class = StoreSerializer

    def get_object(self):
        return Store.objects.get(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        store = self.get_object()
        return Response({
            'id': store.id,
            'name': store.name,
            'address': store.address
        })

class SellerStoreUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]
    serializer_class = StoreSerializer


    def get_object(self):
        return Store.objects.get(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        store = self.get_object()
        data = request.data  # Using request.data instead of json.loads(request.body)
        allowed_fields = ['name', 'address']

        for key, value in data.items():
            if key not in allowed_fields:
                return Response({'detail': f'Cannot update {key}'}, status=status.HTTP_400_BAD_REQUEST)
            if key == 'name' and Store.objects.filter(name=value).exclude(id=store.id).exists():
                return Response({'detail': 'Store name already exists'}, status=status.HTTP_400_BAD_REQUEST)
            setattr(store, key, value)

        store.save()
        return Response({
            'id': store.id,
            'name': store.name,
            'address': store.address
        })

class StoreEmployeeCreateView(generics.CreateAPIView):
    serializer_class = StoreEmployeeCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]

    def get_queryset(self):
        return StoreEmployee.objects.filter(store__owner=self.request.user)

class StoreEmployeeListView(generics.ListAPIView):
    serializer_class = StoreEmployeeCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]

    def get_queryset(self):
        return StoreEmployee.objects.filter(store__owner=self.request.user)

class StoreEmployeeUpdateView(generics.UpdateAPIView):
    serializer_class = StoreEmployeeCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]
    queryset = StoreEmployee.objects.all()
    lookup_field = 'pk'

class StoreEmployeeDeleteView(generics.DestroyAPIView):
    serializer_class = StoreEmployeeCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]
    queryset = StoreEmployee.objects.all()
    lookup_field = 'pk'
