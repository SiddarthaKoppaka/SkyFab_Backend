import csv
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import Product, ProductImage, Category, SubCategory
from .serializers import ProductSerializer


class ImportProductsView(APIView):
    """
    API View to import products from a CSV file and categorize them automatically.
    """
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def parse_product_name(self, product_name):
        """
        Extracts Category, SubCategory, and Product Title from the formatted name:
        Example: "Men_T-Shirts_RoundNeck"
        """
        try:
            category_name, subcategory_name, product_title = product_name.split("_")
        except ValueError:
            category_name, subcategory_name, product_title = "Uncategorized", "Miscellaneous", product_name

        return category_name.strip(), subcategory_name.strip(), product_title.strip()

    def post(self, request, *args, **kwargs):
        """
        Handles CSV file upload and processes products.
        """
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return Response({"error": "Invalid file format. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0
        error_count = 0

        for row in reader:
            try:
                category_name, subcategory_name, product_title = self.parse_product_name(row['Product Name'])

                category, _ = Category.objects.get_or_create(name=category_name)
                subcategory, _ = SubCategory.objects.get_or_create(name=subcategory_name, category=category)

                # Create or update product
                product, created = Product.objects.update_or_create(
                    sku=row['SKU'],
                    defaults={
                        'name': product_title,
                        'design': row.get('Design', ''),
                        'product_type': row.get('Product Type', ''),
                        'price_with_shipping': row['Product & Shipping (Inclusive GST)'],
                        'sizes': row.get('Sizes', ''),
                        'category': category,
                        'subcategory': subcategory,
                    }
                )
                
                # Process and store image URLs
                if 'Image URLs' in row and row['Image URLs']:
                    image_urls = row['Image URLs'].split(',')
                    for image_url in image_urls:
                        ProductImage.objects.get_or_create(product=product, image_url=image_url.strip())

                if created:
                    created_count += 1

            except Exception as e:
                error_count += 1
                continue  # Skip problematic rows without stopping the process

        return Response(
            {
                "success": f"{created_count} products imported successfully",
                "errors": f"{error_count} products had errors and were skipped"
            },
            status=status.HTTP_201_CREATED
        )


class ListProductsView(APIView):
    """
    API View to list all visible products.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(is_visible=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryProductsView(APIView):
    """
    API View to retrieve all products under a specific category.
    """
    permission_classes = [AllowAny]

    def get(self, request, category_name, *args, **kwargs):
        category = get_object_or_404(Category, name__iexact=category_name)
        products = Product.objects.filter(category=category, is_visible=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubCategoryProductsView(APIView):
    """
    API View to retrieve all products under a specific subcategory.
    """
    permission_classes = [AllowAny]

    def get(self, request, category_name, subcategory_name, *args, **kwargs):
        category = get_object_or_404(Category, name__iexact=category_name)
        subcategory = get_object_or_404(SubCategory, name__iexact=subcategory_name, category=category)
        products = Product.objects.filter(subcategory=subcategory, is_visible=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RelatedProductsView(APIView):
    """
    API View to retrieve related products based on a given product ID.
    """
    permission_classes = [AllowAny]

    def get(self, request, product_id, *args, **kwargs):
        # Fetch the product using `serial_number` instead of `id`
        product = get_object_or_404(Product, serial_number=product_id)

        related_products = Product.objects.filter(
            category=product.category,
            subcategory=product.subcategory
        ).exclude(serial_number=product_id)  # Exclude the current product

        # Apply additional filters for closer matches
        if product.product_type:
            related_products = related_products.filter(product_type=product.product_type)

        if product.design:
            # Match based on the first keyword in design for relevance
            related_products = related_products.filter(design__icontains=product.design.split()[0])

        # Limit to 10 related products
        related_products = related_products[:10]

        serializer = ProductSerializer(related_products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

