from django.urls import path,include
from .views import (LoginOTPView,
                    VerifyOTPView,
                    LogOutAPIView,
                    ChangePasswordView,
                    CustomerProfileView,
                    CustomerRegisterView,
                    SellerRegisterView,
                    customer_dashboard,
                    seller_dashboard,
                    ResendOTPView,
                    PhoneLoginView,
                    PhoneVerifyOTPView,
                    CustomerAddressView,
                    CustomerAddressDetailView)
from orders_app.views import (CustomerOrderHistoryView)
from products_app.views import (CommentCreateView,UserCommentsListView)


urlpatterns = [
    path('register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('register/seller/', SellerRegisterView.as_view(), name='seller_register'),
    path('login/email/', LoginOTPView.as_view(), name='email_login'),
    path('login/otp-resend/', ResendOTPView.as_view(), name='otp_resend'),
    path('login/email/verify/', VerifyOTPView.as_view(), name='email_verify_otp'),
    path('login/phone/', PhoneLoginView.as_view(), name='phone_login'),
    path('login/phone/verify/', PhoneVerifyOTPView.as_view(), name='phone_verify_otp'),
    path('logout/', LogOutAPIView.as_view(), name='logout'),
    path('customer/dashboard/profile/', CustomerProfileView.as_view(), name='user_profile'),
    path('customer/dashboard/profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('customer/dashboard/orders/', CustomerOrderHistoryView.as_view(), name='customer_order_history'),
    path('customer/dashboard/address/', CustomerAddressView.as_view(), name='customer_address'),
    path('customer/dashboard/address/<int:pk>/', CustomerAddressDetailView.as_view(), name='customer_address_update'),
    path('customer/dashboard/comments/', UserCommentsListView.as_view(), name='customer_comments'),
    path('customer/dashboard/comments/create/', CommentCreateView.as_view(), name='customer_comments_create'),
]
