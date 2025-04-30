from django.shortcuts import render
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from core_app.custom_permissions import *
from django.views.generic import TemplateView
from users_app.models import CustomUser
from .serializers import (StoreSerializer,
                          StoreEmployeeCreateSerializer,
                          StoreEmployeeSerializer)
from rest_framework import (generics, status, views, permissions, viewsets,serializers)
from rest_framework.response import Response
from .models import Store,StoreEmployee
# Create your views here.

def get_user_store(user):
    if user.groups.filter(name='SellerOwners').exists():
        try:
            return user.store  # Using the related_name="store" from Store model
        except Store.DoesNotExist:
            raise Exception('Store not found')
    try:
        # Access through the user_store related_name from StoreEmployee model
        employee = user.user_store
        # Return the store using store_id field (ForeignKey to Store)
        return employee.store_id
    except StoreEmployee.DoesNotExist:
        raise Exception('Not assigned to a store')


class SellerStoreRetrieveView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]
    serializer_class = StoreSerializer

    def get_object(self):
        return Store.objects.get(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        store = self.get_object()
        return Response({
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'city':store.city,
        })

class SellerStoreUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]
    serializer_class = StoreSerializer


    def get_object(self):
        return Store.objects.get(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        store = self.get_object()
        data = request.data  # Using request.data instead of json.loads(request.body)
        allowed_fields = ['name', 'address','city']

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
            'address': store.address,
            'city': store.city,
        })

class StoreEmployeeCreateView(generics.CreateAPIView):
    serializer_class = StoreEmployeeCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]

    def get_queryset(self):
        return StoreEmployee.objects.filter(store_id__owner=self.request.user)

    def perform_create(self, serializer):
        store = get_user_store(self.request.user)
        serializer.save(store_id=store)

class StoreEmployeeListView(generics.ListAPIView):
    serializer_class = StoreEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]

    def get_queryset(self):
        return StoreEmployee.objects.filter(store_id__owner=self.request.user)

class StoreEmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]
    serializer_class = StoreEmployeeSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        # Only allow operations on employees of the store owned by current user
        try:
            store = Store.objects.get(owner=self.request.user)
            return StoreEmployee.objects.filter(store_id=store).select_related('user_id', 'store_id')
        except Store.DoesNotExist:
            return StoreEmployee.objects.none()

    def perform_update(self, serializer):
        # Prevent changing the store association
        if 'store_id' in serializer.validated_data:
            raise serializers.ValidationError(
                {"store_id": _("Cannot change store association.")}
            )

        # Prevent removing all roles
        instance = self.get_object()
        new_data = serializer.validated_data
        if not new_data.get('is_manager', instance.is_manager) and not new_data.get('is_operator',
                instance.is_operator):
            raise serializers.ValidationError(
                _("Employee must have at least one role (manager or operator).")
            )

        serializer.save()

    def perform_destroy(self, instance):
        # Check if this is the last manager
        if instance.is_manager:
            managers_count = StoreEmployee.objects.filter(
                store_id=instance.store_id,
                is_manager=True
            ).count()
            if managers_count <= 1:
                raise serializers.ValidationError(
                    _("Cannot delete the last manager of the store.")
                )
        instance.delete()

    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)


class StoreListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = StoreSerializer

    def get_queryset(self):
        stores = Store.objects.all()
        return stores

class StoreDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = StoreSerializer

    def get_queryset(self):
        stores = Store.objects.all()
        return stores




class StoreDetailsPageTemplate(TemplateView):
    template_name = 'main/stores_detail.html'

class StoreListTemplate(TemplateView):
    template_name = 'main/stores_page.html'

class StoreDetailTemplate(TemplateView):
    template_name = 'dashboards/seller_dashboard_store.html'

class StoreEmployeeTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_employees.html"

class StoreEmployeeCreateTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_employees_create.html"

class StoreEmployeeEditTemplate(TemplateView):
    template_name = "dashboards/seller_dashboard_employees_edit.html"


