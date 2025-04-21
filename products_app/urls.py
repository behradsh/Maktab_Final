from django.urls import path,include
from .views import (SellerProductListCreateView,SellerProductRetrieveUpdateDestroyView
,CategoryListCreateView,CategoryRetrieveUpdateDestroyView)

urlpatterns = [
    path('seller/dashboard/product/', SellerProductListCreateView.as_view(),name='product_list'),
    path('seller/dashboard/product/<int:pk>/', SellerProductRetrieveUpdateDestroyView.as_view(),name='product_update_delete'),
    path('seller/dashboard/category/', CategoryListCreateView.as_view(), name='category_list'),
    path('seller/dashboard/category/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(),
         name='category_update_delete'),
]