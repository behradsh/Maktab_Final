from django.urls import path,include
from .views import (LoginOTPView,
                    VerifyOTPView,
                    LogOutAPIView,
                    ChangePasswordView,
                    UserDetailView,
                    CustomerRegisterView,
                    SellerRegisterView,
                    customer_dashboard,
                    seller_dashboard,
                    ResendOTPView,)
urlpatterns = [
    path('register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('register/seller/', SellerRegisterView.as_view(), name='seller_register'),
    path('login/otp/', LoginOTPView.as_view(), name='otp_login'),
    path('login/otp-resend/', ResendOTPView.as_view(), name='otp_resend'),
    path('login/verify/', VerifyOTPView.as_view(), name='otp_verify'),
    path('logout/', LogOutAPIView.as_view(), name='logout'),
    path('profile/', UserDetailView.as_view(), name='user_profile'),
    path('profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
]
