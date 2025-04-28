from django.urls import path,include
from .views import (SellerProductListCreateView,SellerProductRetrieveUpdateDestroyView
,CategoryListCreateView,CategoryRetrieveUpdateDestroyView,
                    ProductListHomeView,CategoryListHomeView,
                    CommentCreateView,UserCommentsListView,
                    CustomerCommentsListTemplate,SellerDashboardListProductTemplate,
                    SellerDashboardCreateProductTemplate,SellerDashboardEditProductTemplate,
                    SellerCategoryCreateTemplate,SellerCategoryUpdateTemplate,
                    SellerCategoryListTemplate,)

urlpatterns = [
    path('api/products/', ProductListHomeView.as_view(),name='product_list_home'),
    path('api/category/', CategoryListHomeView.as_view(),name='category_list_home'),
    path('api/seller/dashboard/product/', SellerProductListCreateView.as_view(),name='product_list_api'),
    path('seller/dashboard/product/create/', SellerDashboardCreateProductTemplate.as_view(),name='create_product'),
    path('seller/dashboard/product/', SellerDashboardListProductTemplate.as_view(),name='product_list'),
    path('api/seller/dashboard/product/<int:pk>/', SellerProductRetrieveUpdateDestroyView.as_view(),name='product_update_delete_api'),
    path('seller/dashboard/product/<int:pk>/', SellerDashboardEditProductTemplate.as_view(),name='product_update_delete'),
    path('api/seller/dashboard/category/', CategoryListCreateView.as_view(), name='category_list_api'),
    path('seller/dashboard/category/', SellerCategoryListTemplate.as_view(), name='category_list'),
    path('seller/dashboard/category/create/', SellerCategoryCreateTemplate.as_view(), name='category_create'),
    path('seller/dashboard/category/<int:pk>/', SellerCategoryUpdateTemplate.as_view(), name='category_update'),
    path('api/seller/dashboard/category/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(),
         name='category_update_delete_api'),
    path('api/customer/dashboard/comments/', UserCommentsListView.as_view(), name='customer_comments_api'),
    path('customer/dashboard/comments/', CustomerCommentsListTemplate.as_view(), name='customer_comments'),
    path('api/customer/dashboard/comments/create/', CommentCreateView.as_view(), name='customer_comments_create_api'),
]