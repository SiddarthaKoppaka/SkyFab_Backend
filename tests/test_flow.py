import pytest
from django.urls import reverse


@pytest.fixture
def user_data():
    """Fixture to provide test user data."""
    return {
        "email": "testing@example.com",
        "password": "SecurePassword123",
        "first_name": "Test",
        "last_name": "User",
        "profile": {
            "title": "Mr",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street",
            "country": "IN",
            "city": "TestCity",
            "zip": "12345",
        },
    }

@pytest.mark.django_db
def test_user_flow(client, user_data):
    # Step 1: Register User
    register_url = reverse('register')
    register_response = client.post(register_url, data=user_data, content_type="application/json")
    assert register_response.status_code == 201, f"Register Response: {register_response.content.decode()}"
    register_data = register_response.json()
    assert "access" in register_data and "refresh" in register_data, f"Register Response: {register_data}"
    access_token = register_data["access"]
    refresh_token = register_data["refresh"]

    # Step 2: Login User
    login_url = reverse('login')
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_response = client.post(login_url, data=login_data, content_type="application/json")
    assert login_response.status_code == 200, f"Login Response: {login_response.content.decode()}"
    login_response_data = login_response.json()
    assert "access" in login_response_data and "refresh" in login_response_data, f"Login Response: {login_response_data}"

    # Step 3: Add Products to Cart
    add_to_cart_url = reverse('add-to-cart')  # Update with your endpoint
    product_data_1 = {"product_id": 1, "quantity": 2}  # Adjust product details
    product_data_2 = {"product_id": 2, "quantity": 1}  # Add another product

    auth_header = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

    # Add first product to the cart
    add_to_cart_response_1 = client.post(add_to_cart_url, data=product_data_1, content_type="application/json", **auth_header)
    assert add_to_cart_response_1.status_code == 201, f"Add to Cart Response (Product 1): {add_to_cart_response_1.content.decode()}"

    # Add second product to the cart
    add_to_cart_response_2 = client.post(add_to_cart_url, data=product_data_2, content_type="application/json", **auth_header)
    assert add_to_cart_response_2.status_code == 201, f"Add to Cart Response (Product 2): {add_to_cart_response_2.content.decode()}"

    # Step 4: View Cart
    cart_url = reverse('cart')  # Update the endpoint as per your application
    view_cart_response = client.get(cart_url, **auth_header)
    assert view_cart_response.status_code == 200, f"View Cart Response: {view_cart_response.content.decode()}"

    cart_data = view_cart_response.json()
    assert "cart_items" in cart_data, f"View Cart Response Missing Cart Items: {cart_data}"
    assert len(cart_data["cart_items"]) > 0, "Cart is empty after adding products"
    print(f"Cart Items: {cart_data['cart_items']}")

    # Step 5: Refresh Token
    refresh_url = reverse('token_refresh')  # Update this if your refresh endpoint is named differently
    refresh_data = {"refresh": refresh_token}
    refresh_response = client.post(refresh_url, data=refresh_data, content_type="application/json")
    assert refresh_response.status_code == 200, f"Refresh Response: {refresh_response.content.decode()}"
    new_access_token = refresh_response.json().get("access")
    assert new_access_token, "Failed to retrieve new access token"

    # Step 7: Place Order
    place_order_url = reverse('place_order')  # Update this endpoint
    order_data = {
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "address1": "123 Test Street",
        "city": "TestCity",
        "zip": "12345",
        "country": "IN",
    }
    place_order_response = client.post(place_order_url, data=order_data, content_type="application/json", **auth_header)
    assert place_order_response.status_code == 201, f"Place Order Response: {place_order_response.content.decode()}"

    # Step 8: Logout
    logout_url = reverse('logout')  # Update if different
    logout_response = client.post(logout_url, **auth_header)
    assert logout_response.status_code == 200, f"Logout Response: {logout_response.content.decode()}"
