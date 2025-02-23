from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from products.models import Product  # Assuming Product model is defined in the products app
from django.conf import settings
import requests
import decimal
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Utility to get access token from Qikink
def get_access_token():
    url = "https://sandbox.qikink.com/api/token"
    client_id = "413721902814506"
    client_secret = "51fcf1bc9e32215e9f2caec4d0231eb0beb6c164d28886edb7ccf7d531056ea5"

    payload = {
        'ClientId': client_id,
        'client_secret': client_secret
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data.get('Accesstoken')

        if access_token:
            return access_token
        else:
            raise Exception("Access token not found in the response")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while requesting the access token: {e}")
        return None

# Cache the access token
def store_access_token():
    access_token = get_access_token()
    if access_token:
        cache.set('qikink_access_token', access_token, timeout=3600)

# API view to place an order
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique order number
        order_number = 234

        # Prepare line_items for API call
        line_items = []
        for item in cart.items.all():
            product = item.product  # Assuming `CartItem` has a ForeignKey to Product model
            line_items.append({
                "search_from_my_products": 1,  # Set to 1 as we are searching by SKU
                "sku": product.sku,  # SKU from Product model
                "quantity": str(item.quantity),
                "price": str(float(item.get_total_price())),
                "designs": []  # Empty because we are using existing SKUs from My Products
            })

        # Calculate total order value
        total_order_value = sum(item.get_total_price() for item in cart.items.all())

        # Prepare payload for API
        payload = {
            "order_number": order_number,
            "qikink_shipping": "1",  # Use Qikink's shipping
            "gateway": "COD",  # Change to "PREPAID" if required
            "total_order_value": str(float(total_order_value)),
            "line_items": line_items,
            "add_ons": [
                {
                    "box_packing": 1,
                    "gift_wrap": 0,
                    "rush_order": 1,
                    "custom_letter": "www.sample_contents.com"
                }
            ],
            "shipping_address": {
                "first_name": request.data.get("first_name"),
                "last_name": request.data.get("last_name", ""),
                "address1": request.data.get("address1"),
                "phone": request.data.get("phone"),
                "email": request.data.get("email"),
                "city": request.data.get("city"),
                "zip": request.data.get("zip"),
                "province": request.data.get("province"),
                "country_code": request.data.get("country_code"),
            }
        }

        # Retrieve access token from cache or request a new one
        access_token = cache.get('qikink_access_token') or get_access_token()
        if not access_token:
            return Response({"error": "Failed to retrieve access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            "ClientId": "413721902814506",
            "Accesstoken": access_token,
        }

        # Send order creation request to Qikink API
        try:
            logger.info(f"Payload: {payload}")
            logger.info(f"Headers: {headers}")

            response = requests.post("https://sandbox.qikink.com/api/order/create", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("message") == "Order created successfully":
                tracking_url = data.get("tracking_url")

                # Create Order in the database
                order = Order.objects.create(
                    user=user,
                    order_number=order_number,
                    total_order_value=decimal.Decimal(total_order_value),
                    tracking_url=tracking_url,
                )
                for item in cart.items.all():
                    OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

                # Clear the cart
                cart.items.all().delete()

                return Response({"message": "Order placed successfully", "tracking_url": tracking_url}, status=status.HTTP_201_CREATED)

            else:
                logger.error(f"Order placement failed: {data}")
                return Response({"error": "Order placement failed", "details": data}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logger.error(f"API Error Response: {e.response.text}")
            logger.error(f"Failed to place order: {e}")
            return Response({"error": "Failed to place order", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
