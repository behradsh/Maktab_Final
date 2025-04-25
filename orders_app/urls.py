from django.urls import path,include
from .views import (AddToCartAPIView, UpdateCartAPIView, CartCountAPIView,
                    RemoveFromCartAPIView, CustomerAddressesAPIView, AddAddressAPIView,
                    SubmitOrderAPIView, OrdersListAPIView)





urlpatterns = [
    path('api/add-to-cart/', AddToCartAPIView.as_view(), name='add_to_cart'),
    path('api/cart-count/', CartCountAPIView.as_view(), name='get_cart_count'),
    path('api/update-cart/', UpdateCartAPIView.as_view(), name='update_cart'),
    path('api/remove-cart/', RemoveFromCartAPIView.as_view(), name='remove_cart_item'),
    path('api/customer-addresses/', CustomerAddressesAPIView.as_view(), name='customer_addresses'),
    path('api/customer-addresses/add', AddAddressAPIView.as_view(), name='add_customer_addresses'),
    path('api/list-order/', OrdersListAPIView.as_view(), name='order_list'),
    path('api/submit-order/', SubmitOrderAPIView.as_view(), name='submit_order'),
]