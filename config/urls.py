from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view as yasg_schema_view

# DRF OpenAPI Schema View
drf_schema_view = get_schema_view(
    title="Skyfab Backend REST API",
    description="OpenAPI schema for Skyfab's backend APIs.",
    version="1.0.0",
    public=True,
    permission_classes=[AllowAny],  # Allow anyone to view the schema
)


urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # User Authentication APIs
    path('api/v1/users/', include('users.urls')),

    # Product Management APIs
    path('api/v1/products/', include('products.urls')),

    # Cart Management APIs
    path('api/v1/cart/', include('cart.urls')),

    # Order Management APIs
    path('api/v1/orders/', include('orders.urls')),

    # DRF API Schema & Docs
    path('api/docs/', include_docs_urls(title="Skyfab API Documentation")),
    path('api/schema/', drf_schema_view, name="api-schema"),  # DRF OpenAPI schema (JSON)

]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
