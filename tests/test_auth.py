import pytest
from django.urls import reverse

@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
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
def test_register_user(client, user_data):
    register_url = reverse('register')
    response = client.post(register_url, data=user_data, content_type="application/json")
    assert response.status_code == 201, f"Response: {response.content.decode()}"
    response_data = response.json()
    assert "refresh" in response_data, f"Response: {response_data}"
    assert "access" in response_data, f"Response: {response_data}"
    assert "user" in response_data, f"Response: {response_data}"


@pytest.mark.django_db
def test_login_user(client, user_data):
    # Register the user first
    register_url = reverse('register')
    client.post(register_url, data=user_data, content_type="application/json")

    # Login the user
    login_url = reverse('login')
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post(login_url, data=login_data, content_type="application/json")
    assert response.status_code == 200, f"Response: {response.content.decode()}"
    response_data = response.json()
    assert "refresh" in response_data, f"Response: {response_data}"
    assert "access" in response_data, f"Response: {response_data}"
    assert "user" in response_data, f"Response: {response_data}"