from django.db import models

class Category(models.Model):
    """
    Model representing a product category.
    """
    name = models.CharField(max_length=100, unique=True)
    is_accessory = models.BooleanField(default=False, help_text="Indicates if the category is an accessory.")

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """
    Model representing a subcategory of a product category.
    """
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='subcategories'
    )
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model representing a product with Google Drive image support.
    """
    serial_number = models.AutoField(primary_key=True)
    product_id = models.CharField(
        max_length=50, unique=True, blank=True, null=True, 
        help_text="Unique product identifier. Auto-generated if left blank."
    )
    name = models.CharField(max_length=255, help_text="Name of the product.")
    design = models.CharField(max_length=255, blank=True, null=True, help_text="Design name or variant.")
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit (SKU).")
    product_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of product (e.g., T-shirt, Mug).")
    price_with_shipping = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price including shipping and GST."
    )
    sizes = models.CharField(
        max_length=255, blank=True, null=True, 
        help_text="Available sizes, comma-separated (e.g., S,M,L,XL)."
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='products'
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.SET_NULL, null=True, related_name='products'
    )
    is_visible = models.BooleanField(default=True, help_text="Determines if the product is visible on the store.")

    def save(self, *args, **kwargs):
        """
        Auto-generate product_id if not provided.
        """
        if not self.product_id:
            self.product_id = f"PROD-{self.serial_number or ''}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    Model to store product images as Google Drive URLs.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image_url = models.URLField(
        max_length=500, blank=True, null=True, help_text="Google Drive image URL."
    )  # ✅ Temporarily allowing null values

    def __str__(self):
        return f"Image for {self.product.name}"

