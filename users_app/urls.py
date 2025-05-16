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
                    CustomerDashboardTemplate,
                    SellerProfileView,
                    SellerChangePasswordView,
                    HomeView,CustomerChangePasswordTemplate,
CustomerOrdersListTemplate,CustomerAddressListTemplate,
CustomerAddressEditTemplate,CustomerAddressCreateTemplate,
CustomerRegisterTemplate,SellerRegisterTemplate,HomeTemplate,
SellerDashboardTemplate,SellerDashboardChangePassTemplate,
SellerOrderListView,SellerOrderUpdateView,SellerDashboardOrdersTemplate,
SellerDashboardOrdersEditTemplate,CustomerOrderDetailsTemplate,
HomePersianTemplate,SellerDashboardReportsTemplate,SellerReportsView,
                    )
from orders_app.views import (CustomerOrderHistoryView,CustomerOrderDetailsView)
from products_app.views import (CommentCreateView, UserCommentsListView)
from store_app.views import (SellerStoreRetrieveView,
                             SellerStoreUpdateView, )
from products_app.views import (SellerProductListCreateView, SellerProductRetrieveUpdateDestroyView,
                                CategoryListCreateView, CategoryRetrieveUpdateDestroyView)


def is_customer(user):
    return user.is_customer


def is_seller(user):
    return not user.is_customer


router = DefaultRouter()
# router.register(r'customer', CustomerPanelViewSet, basename='customer')
# router.register(r'seller', SellerPanelViewSet, basename='seller')


urlpatterns = [
    # path('', HomeView.as_view(), name='home_page_api'),
    path('', HomeTemplate.as_view(), name='home_page'),
    path('', HomePersianTemplate.as_view(), name='home_page_fa'),
    path('api/seller/dashboard/profile/', SellerProfileView.as_view(), name='seller_dashboard_api'),
    path('seller/dashboard/', SellerDashboardTemplate.as_view(), name='seller_dashboard'),
    path('api/register/customer/', CustomerRegisterView.as_view(), name='customer_register_api'),
    path('register/customer/', CustomerRegisterTemplate.as_view(), name='customer_register'),
    path('api/register/seller/', SellerRegisterView.as_view(), name='seller_register_api'),
    path('register/seller/', SellerRegisterTemplate.as_view(), name='seller_register'),
    path('api/login/email/', LoginOTPView.as_view(), name='email_login'),
    path('api/login/otp-resend/', ResendOTPView.as_view(), name='otp_resend'),
    path('api/login/email/verify/', VerifyOTPView.as_view(), name='email_verify_otp'),
    path('api/login/phone/', PhoneLoginView.as_view(), name='phone_login'),
    path('api/login/phone/verify/', PhoneVerifyOTPView.as_view(), name='phone_verify_otp'),
    path('api/logout/', LogOutAPIView.as_view(), name='logout'),
    path('api/customer/dashboard/profile/', CustomerProfileView.as_view(), name='user_dashboard_profile'),
    path('customer/dashboard/', CustomerDashboardTemplate.as_view(), name='customer_dashboard_profile'),
    path('api/customer/dashboard/profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('customer/dashboard/change_password/', CustomerChangePasswordTemplate.as_view(), name='customer_change_password'),
    path('api/customer/dashboard/orders/', CustomerOrderHistoryView.as_view(), name='customer_orders_api'),
    path('api/customer/dashboard/orders/<int:pk>/', CustomerOrderDetailsView.as_view(), name='customer_orders_details_api'),
    path('customer/dashboard/orders/', CustomerOrdersListTemplate.as_view(), name='customer_order_history'),
    path('customer/dashboard/orders/<int:pk>/', CustomerOrderDetailsTemplate.as_view(), name='customer_order_details'),
    path('api/customer/dashboard/address/', CustomerAddressView.as_view(), name='customer_address'),
    path('customer/dashboard/address/create/', CustomerAddressCreateTemplate.as_view(), name='customer_address_create'),
    path('customer/dashboard/address/', CustomerAddressListTemplate.as_view(), name='customer_address_list'),
    path('api/customer/dashboard/address/<int:pk>/', CustomerAddressDetailView.as_view(),
         name='customer_address_update_api'),
    path('customer/dashboard/address/<int:pk>/', CustomerAddressEditTemplate.as_view(),
         name='customer_address_update'),
    path('api/seller/dashboard/profile/change_password/', SellerChangePasswordView.as_view(),
         name='change_password_seller_api'),
    path('seller/dashboard/profile/change_password/', SellerDashboardChangePassTemplate.as_view(),
         name='change_password_seller'),
    path('api/seller/dashboard/orders/', SellerOrderListView.as_view(),
         name='seller_orders_api'),
    path('api/seller/dashboard/orders/<int:pk>/', SellerOrderUpdateView.as_view(),
         name='seller_orders_edit_api'),
    path('seller/dashboard/orders/', SellerDashboardOrdersTemplate.as_view(),
         name='seller_orders'),
    path('seller/dashboard/orders/<int:pk>/', SellerDashboardOrdersEditTemplate.as_view(),
         name='seller_orders_edit'),
    path('api/seller/dashboard/report/', SellerReportsView.as_view(),
         name='seller_reports_api'),
    path('seller/dashboard/report/', SellerDashboardReportsTemplate.as_view(),
         name='seller_reports'),

    # path('', include(router.urls)),
]
