from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    path('seller/dashboard/profile/', SellerProfileView.as_view(), name='seller_dashboard'),
    path('register/customer/', CustomerRegisterView.as_view(), name='customer_register'),
    path('register/seller/', SellerRegisterView.as_view(), name='seller_register'),
    path('login/email/', LoginOTPView.as_view(), name='email_login'),
    path('login/otp-resend/', ResendOTPView.as_view(), name='otp_resend'),
    path('login/email/verify/', VerifyOTPView.as_view(), name='email_verify_otp'),
    path('login/phone/', PhoneLoginView.as_view(), name='phone_login'),
    path('login/phone/verify/', PhoneVerifyOTPView.as_view(), name='phone_verify_otp'),
    path('logout/', LogOutAPIView.as_view(), name='logout'),
    path('customer/dashboard/profile/', CustomerProfileView.as_view(), name='user_dashboard_profile'),
    path('customer/dashboard/profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('customer/dashboard/orders/', CustomerOrderHistoryView.as_view(), name='customer_order_history'),
    path('customer/dashboard/address/', CustomerAddressView.as_view(), name='customer_address'),
    path('customer/dashboard/address/<int:pk>/', CustomerAddressDetailView.as_view(), name='customer_address_update'),
    path('seller/dashboard/profile/change_password/', SellerChangePasswordView.as_view(), name='change_password_seller'),
    # path('', include(router.urls)),
]