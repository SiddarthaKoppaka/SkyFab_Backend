from django.urls import path
from .views import (
    ImportProductsView, 
    ListProductsView, 
    CategoryProductsView, 
    SubCategoryProductsView, 
    RelatedProductsView
)

urlpatterns = [
    # Bulk Import Products via CSV
    path('import/', ImportProductsView.as_view(), name='import-products'),
    
    # List all available products
    path('', ListProductsView.as_view(), name='list-products'),

    # Retrieve products by category
    path('category/<str:category_name>/', CategoryProductsView.as_view(), name='category-products'),

    # Retrieve products by subcategory within a category
    path('category/<str:category_name>/<str:subcategory_name>/', SubCategoryProductsView.as_view(), name='subcategory-products'),

    # Retrieve related products based on a given product ID
    path('related/<int:product_id>/', RelatedProductsView.as_view(), name='related-products'),
]
