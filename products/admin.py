import csv
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from .models import Product, Category, SubCategory, ProductImage


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for managing product images.
    """
    model = ProductImage
    extra = 1  # Show one empty image URL field by default
    fields = ['image_url']


class ProductAdmin(admin.ModelAdmin):
    """
    Admin panel for managing products, automated CSV processing, and Google Drive image linking.
    """
    list_display = ('name', 'sku', 'category', 'subcategory', 'price_with_shipping', 'is_visible')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'subcategory', 'is_visible')
    change_list_template = "admin/products/change_list.html"  # Custom template for admin bulk operations
    inlines = [ProductImageInline]  # Enable inline product images management

    def parse_product_name(self, product_name):
        """
        Extracts Category, SubCategory, and Product Title from the formatted name:
        Example: "Cotton_T-Shirts_RoundNeck"
        """
        try:
            category_name, subcategory_name, product_title = product_name.split("_")
        except ValueError:
            category_name, subcategory_name, product_title = "Uncategorized", "Miscellaneous", product_name

        return category_name, subcategory_name, product_title

    def generate_drive_links(self, category, subcategory, product_title):
        """
        Generates a structured Google Drive image folder URL.
        Example: `/Cotton_Apparels/T-Shirts/RoundNeck/images`
        """
        base_drive_url = settings.GOOGLE_DRIVE_BASE_URL  # Ensure this is set in `settings.py`
        return f"{base_drive_url}/{category}/{subcategory}/{product_title}/images"

    def get_urls(self):
        """
        Adds custom URL for uploading products via CSV in the Django Admin panel.
        """
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv_view), name='product-upload-csv'),
        ]
        return custom_urls + urls

    def upload_csv_view(self, request):
        """
        Custom admin view to process bulk product uploads via CSV.
        """
        if request.method == "POST":
            csv_file = request.FILES.get('file')
            if not csv_file.name.endswith('.csv'):
                self.message_user(request, "Please upload a valid CSV file.", level=messages.ERROR)
                return HttpResponseRedirect(request.path)

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            try:
                for row in reader:
                    # Parse product name into category, subcategory, and title
                    category_name, subcategory_name, product_title = self.parse_product_name(row['Product Name'])

                    # Create or fetch Category and SubCategory
                    category, _ = Category.objects.get_or_create(name=category_name)
                    subcategory, _ = SubCategory.objects.get_or_create(name=subcategory_name, category=category)

                    # Create product entry
                    product, created = Product.objects.get_or_create(
                        name=product_title,
                        sku=row['SKU'],
                        product_type=row.get('Product Type', ''),
                        price_with_shipping=row['Product & Shipping (Inclusive GST)'],
                        sizes=row.get('Sizes', ''),
                        category=category,
                        subcategory=subcategory,
                    )

                    # Generate structured Google Drive folder URL
                    drive_link_base = self.generate_drive_links(category_name, subcategory_name, product_title)

                    # Store image links if provided
                    if 'Image URLs' in row and row['Image URLs']:
                        image_urls = row['Image URLs'].split(',')
                        for image_url in image_urls:
                            ProductImage.objects.create(product=product, image_url=f"{drive_link_base}/{image_url.strip()}")

                self.message_user(request, "CSV file imported successfully!", level=messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Error processing file: {e}", level=messages.ERROR)

            return HttpResponseRedirect("../")  # Redirect back to the product list

        return render(request, 'admin/csv_upload.html', {})

    upload_csv_view.short_description = "Upload Products via CSV"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_accessory']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin panel for managing product images, using Google Drive URLs.
    """
    list_display = ['product', 'image_preview']

    def image_preview(self, obj):
        """Display the image URL as a clickable link in Django Admin."""
        return obj.image_url
    image_preview.short_description = "Image URL"


admin.site.register(Product, ProductAdmin)
