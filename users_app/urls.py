from django.urls import path,include
from .views import (LoginAPIView,
                    LogOutAPIView,
                    ChangePasswordView,
                    UserDetailView,
                    CustomerRegisterView,
                    SellerRegisterView,
                    customer_dashboard,
                    seller_dashboard)
urlpatterns = [
    path('register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('register/seller/', SellerRegisterView.as_view(), name='seller_register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogOutAPIView.as_view(), name='logout'),
    path('profile/', UserDetailView.as_view(), name='user_profile'),
    path('profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
]
