from django.urls import path
from .views import AddToCartView, ViewCartView

urlpatterns = [
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('', ViewCartView.as_view(), name='cart'),
]
