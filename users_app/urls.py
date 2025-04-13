from django.urls import path,include
from .views import CustomerRegistrationView,SellerRegistrationView,LoginAPIView,LogOutAPIView
urlpatterns = [
    path('register/customer', CustomerRegistrationView.as_view(), name='customer_register'),
    path('register/seller', SellerRegistrationView.as_view(), name='seller_register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogOutAPIView.as_view(), name='logout'),
]