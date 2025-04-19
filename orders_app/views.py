from django.shortcuts import render
from rest_framework import viewsets, permissions,generics
from .models import Orders,OrderItems
from .serializers import OrderSerializer,OrderItemSerializer
# Create your views here.

class CustomerOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Orders.objects.filter(customer=self.request.user)
