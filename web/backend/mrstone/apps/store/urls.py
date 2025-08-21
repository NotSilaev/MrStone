from django.urls import path

from apps.store import views


urlpatterns = [
    path('products/categories/', views.CategoryList.as_view(), name='category_list'),
    path('products/categories/<str:category_slug>/', views.CategoryDetail.as_view(), name='category_detail'),
    path('products/', views.ProductList.as_view(), name='product_list'),
    path('products/<str:product_slug>/', views.ProductDetail.as_view(), name='product_detail'),
]
