from django.urls import path,include
from .views import (SellerStoreRetrieveView,SellerStoreUpdateView,StoreEmployeeCreateView,
                    StoreEmployeeListView,
StoreEmployeeRetrieveUpdateDestroyView,StoreDetailTemplate,StoreEmployeeTemplate,
StoreEmployeeCreateTemplate,StoreEmployeeEditTemplate,StoreListView,StoreListTemplate,StoreDetailView,
StoreDetailsPageTemplate,
                    )


urlpatterns = [
    path('api/stores/', StoreListView.as_view(),name='store_list_api'),
    path('stores/', StoreListTemplate.as_view(),name='store_list_page'),
    path('api/stores/<int:pk>/', StoreDetailView.as_view(),name='store_detail_api'),
    path('stores/<int:pk>/', StoreDetailsPageTemplate.as_view(),name='store_detail_page'),
    path('api/seller/dashboard/store/', SellerStoreRetrieveView.as_view(),name='seller_store_api'),
    path('seller/dashboard/store/', StoreDetailTemplate.as_view(),name='seller_store'),
    path('api/seller/dashboard/store/<int:pk>/', SellerStoreUpdateView.as_view(),name='seller_store_update_api'),
    path('api/seller/dashboard/employee/', StoreEmployeeListView.as_view(),name='employee_list_api'),
    path('seller/dashboard/employee/', StoreEmployeeTemplate.as_view(),name='employee_list'),
    path('api/seller/dashboard/employee/create/', StoreEmployeeCreateView.as_view(),name='employee_create_api'),
    path('seller/dashboard/employee/create/', StoreEmployeeCreateTemplate.as_view(),name='employee_create'),
    path('api/seller/dashboard/employee/<int:pk>/', StoreEmployeeRetrieveUpdateDestroyView.as_view(),name='employee_update_api'),
    path('seller/dashboard/employee/<int:pk>/', StoreEmployeeEditTemplate.as_view(),name='employee_update'),

]

