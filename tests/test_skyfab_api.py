import pytest
from django.urls import reverse

@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
        "phone_number" : "+919394029313",
        "password": "SecurePassword123",
        "first_name": "Test",
        "last_name": "User",
        "profile": {
            "title": "Mr",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street",
            "country": "IN",
            "city": "TestCity",
            "zip": "12345"
        }
    }

@pytest.mark.django_db
def test_user_workflow(client, user_data):
    """
    End-to-end test for user registration, login, profile creation,
    product browsing, searching, adding to cart, ordering, and logging out.
    """
    # Step 1: Register User
    register_url = reverse('register')
    register_response = client.post(register_url, data=user_data, content_type="application/json")
    assert register_response.status_code == 201, f"Register Response: {register_response.content.decode()}"
    register_data = register_response.json()
    access_token = register_data["access"]
    refresh_token = register_data["refresh"]
    
    # Step 2: Login User
    login_url = reverse('login')
    login_response = client.post(login_url, data={"phone_number": user_data["phone_number"], "password": user_data["password"]}, content_type="application/json")
    assert login_response.status_code == 200, f"Login Response: {login_response.content.decode()}"
    login_data = login_response.json()
    
    # Step 3: View Product List
    products_url = reverse('list-products')
    products_response = client.get(products_url, HTTP_AUTHORIZATION=f'Bearer {access_token}')
    assert products_response.status_code == 200, "Failed to fetch product list"
    
    # Step 5: Add Product to Cart
    product_id = products_response.json()[0]['serial_number']
    add_to_cart_url = reverse('add-to-cart')
    add_to_cart_response = client.post(add_to_cart_url, data={"product_id": product_id, "quantity": 1}, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {access_token}')
    assert add_to_cart_response.status_code == 201, "Failed to add product to cart"
    
    # Step 6: Place Order
    place_order_url = reverse('place-order')
    place_order_response = client.post(place_order_url, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {access_token}')
    assert place_order_response.status_code == 201, "Order placement failed"
    
    # Step 7: Logout
    logout_url = reverse('logout')
    logout_response = client.post(logout_url, data={"refresh": refresh_token}, content_type="application/json")
    assert logout_response.status_code == 200, "Logout failed"
    
    # Step 8: Password Reset
    forgot_password_url = reverse('forgot-password')
    forgot_password_response = client.post(forgot_password_url, data={"email": user_data["email"]}, content_type="application/json")
    assert forgot_password_response.status_code == 200, "Forgot password request failed"