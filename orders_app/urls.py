from django.urls import path, include
from .views import (CustomerAddressesAPIView, AddAddressAPIView,
                    OrdersListAPIView,
                    CheckoutView)

urlpatterns = [
path('api/checkout/', CheckoutView.as_view(), name='checkout_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('customer-addresses/', CustomerAddressesAPIView.as_view(), name='customer_addresses'),
    path('customer-addresses/add', AddAddressAPIView.as_view(), name='add_customer_addresses'),
    path('list-order/', OrdersListAPIView.as_view(), name='order_list'),
#     path('submit-order/', SubmitOrderAPIView.as_view(), name='submit_order'),
]
