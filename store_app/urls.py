from django.urls import path,include
from .views import (SellerStoreRetrieveView,SellerStoreUpdateView,StoreEmployeeCreateView,
                    StoreEmployeeListView,
StoreEmployeeRetrieveUpdateDestroyView,
                    )


urlpatterns = [
    path('api/seller/dashboard/store/', SellerStoreRetrieveView.as_view(),name='seller_store'),
    path('api/seller/dashboard/store/<int:pk>/', SellerStoreUpdateView.as_view(),name='seller_store_update'),
    path('api/seller/dashboard/employee/', StoreEmployeeListView.as_view(),name='employee_list'),
    path('api/seller/dashboard/employee/create/', StoreEmployeeCreateView.as_view(),name='employee_create'),
    path('api/seller/dashboard/employee/<int:pk>/', StoreEmployeeRetrieveUpdateDestroyView.as_view(),name='employee_update'),

]

