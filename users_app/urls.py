from tempfile import template

from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
# import django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from .views import (LoginOTPView,
                    VerifyOTPView,
                    LogOutAPIView,
                    ChangePasswordView,
                    CustomerProfileView,
                    CustomerRegisterView,
                    SellerRegisterView,
                    ResendOTPView,
                    PhoneLoginView,
                    PhoneVerifyOTPView,
                    CustomerAddressView,
                    CustomerAddressDetailView,
    #CustomerPanelViewSet,
SellerProfileView,
SellerChangePasswordView,
HomeView,
    )
from orders_app.views import (CustomerOrderHistoryView)
from products_app.views import (CommentCreateView,UserCommentsListView)
from store_app.views import (SellerStoreRetrieveView,
                             SellerStoreUpdateView,)
from products_app.views import (SellerProductListCreateView, SellerProductRetrieveUpdateDestroyView,
    CategoryListCreateView,CategoryRetrieveUpdateDestroyView)

def is_customer(user):
    return user.is_customer

def is_seller(user):
    return not user.is_customer


router = DefaultRouter()
# router.register(r'customer', CustomerPanelViewSet, basename='customer')
# router.register(r'seller', SellerPanelViewSet, basename='seller')



urlpatterns = [
    path('', HomeView.as_view(), name='home_page'),
    path('api/seller/dashboard/profile/', SellerProfileView.as_view(), name='seller_dashboard'),
    path('api/register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('api/register/seller/', SellerRegisterView.as_view(), name='seller_register'),
    path('api/login/email/', LoginOTPView.as_view(), name='email_login'),
    path('api/login/otp-resend/', ResendOTPView.as_view(), name='otp_resend'),
    path('api/login/email/verify/', VerifyOTPView.as_view(), name='email_verify_otp'),
    path('api/login/phone/', PhoneLoginView.as_view(), name='phone_login'),
    path('api/login/phone/verify/', PhoneVerifyOTPView.as_view(), name='phone_verify_otp'),
    path('api/logout/', LogOutAPIView.as_view(), name='logout'),
    path('api/customer/dashboard/profile/', CustomerProfileView.as_view(), name='user_dashboard_profile'),
    path('api/customer/dashboard/profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/customer/dashboard/orders/', CustomerOrderHistoryView.as_view(), name='customer_order_history'),
    path('customer/dashboard/orders/', TemplateView.as_view(), name='customer_order_history'),
    # path('api/customer/dashboard/address/', CustomerAddressView.as_view(), name='customer_address'),
    path('api/customer/dashboard/address/<int:pk>/', CustomerAddressDetailView.as_view(), name='customer_address_update'),
    path('api/seller/dashboard/profile/change_password/', SellerChangePasswordView.as_view(), name='change_password_seller'),
    # path('', include(router.urls)),
]