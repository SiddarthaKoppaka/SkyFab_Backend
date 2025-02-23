from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer

class AddToCartView(APIView):
    
    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        # Ensure quantity is positive
        if not isinstance(quantity, int) or quantity <= 0:
            return Response({"error": "Quantity must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch product using `serial_number`
        product = Product.objects.filter(product_id=product_id, is_visible=True).first()
        if not product:
            return Response({"error": "Product not found or not visible"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create a cart for the user
        cart, _ = Cart.objects.get_or_create(user=user)

        # Get or create the cart item and update quantity
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Product added to cart"}, status=status.HTTP_201_CREATED)


class ViewCartView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
