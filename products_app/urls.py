from django.urls import path,include
from .views import (SellerProductListCreateView,SellerProductRetrieveUpdateDestroyView
,CategoryListCreateView,CategoryRetrieveUpdateDestroyView,
                    ProductListHomeView,CategoryListHomeView,
                    CommentCreateView,UserCommentsListView)

urlpatterns = [
    path('api/products/', ProductListHomeView.as_view(),name='product_list_home'),
    path('api/category/', CategoryListHomeView.as_view(),name='category_list_home'),
    path('seller/dashboard/product/', SellerProductListCreateView.as_view(),name='product_list'),
    path('seller/dashboard/product/<int:pk>/', SellerProductRetrieveUpdateDestroyView.as_view(),name='product_update_delete'),
    path('seller/dashboard/category/', CategoryListCreateView.as_view(), name='category_list'),
    path('seller/dashboard/category/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(),
         name='category_update_delete'),
    path('customer/dashboard/comments/', UserCommentsListView.as_view(), name='customer_comments'),
    path('customer/dashboard/comments/create/', CommentCreateView.as_view(), name='customer_comments_create'),

]