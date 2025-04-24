from django.urls import path,include
from .views import CartView,CartItemUpdateView,CartItemDeleteView,CheckoutView
urlpatterns = [
path('cart/',CartView.as_view(),name='cart'),
path('cart/items/<int:pk>/',CartItemUpdateView.as_view(),name='cart_item_update'),
path('cart/items/<int:pk>/delete',CartItemDeleteView.as_view(),name='cart_item_delete'),
path('checkout/',CheckoutView.as_view(),name='checkout'),
path('seller/dashboard/orders/',CheckoutView.as_view(),name='store_orders'),
path('seller/dashboard/orders/<int:pk>/',CheckoutView.as_view(),name='store_orders'),
]