from django.urls import path,include
from .views import (SellerStoreRetrieveView,SellerStoreUpdateView,StoreEmployeeCreateView,
                    StoreEmployeeListView,StoreEmployeeUpdateView,StoreEmployeeDeleteView,
                    )


urlpatterns = [
    path('seller/dashboard/store/', SellerStoreRetrieveView.as_view(),name='seller_store'),
    path('seller/dashboard/store/<int:pk>/', SellerStoreUpdateView.as_view(),name='seller_store_update'),
    path('seller/dashboard/employee/', StoreEmployeeListView.as_view(),name='employee_list'),
    path('seller/dashboard/employee/create/', StoreEmployeeCreateView.as_view(),name='employee_create'),
    path('seller/dashboard/employee/<int:pk>/', StoreEmployeeUpdateView.as_view(),name='employee_update'),
    path('seller/dashboard/employee/<int:pk>/delete/', StoreEmployeeDeleteView.as_view(),name='employee_delete'),

]

