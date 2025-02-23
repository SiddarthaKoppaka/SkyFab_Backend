from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import (
    UserViewSet, RegisterView, LoginView, LogoutView, 
    ForgotPasswordView, ResetPasswordView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Authentication Routes
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Password Reset Routes
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]

"""
📌 **API Documentation for Users App**
---
### 🔐 **Authentication APIs**
1. **`POST /register/`** - Register a new user with phone number & email.
2. **`POST /login/`** - Log in using phone number or email.
3. **`POST /logout/`** - Log out & blacklist the JWT token.

### 🔑 **Password Reset APIs**
4. **`POST /forgot-password/`** - Request an OTP for password reset via email or phone.
5. **`POST /reset-password/`** - Reset the password after OTP verification.

### 👤 **User Management APIs**
6. **`GET /users/`** - Retrieve a list of all users (Admin only).
7. **`POST /users/`** - Create a new user (Admin only).
8. **`GET /users/{id}/`** - Retrieve user details.
9. **`PUT /users/{id}/`** - Update user details.
10. **`DELETE /users/{id}/`** - Delete a user (Admin only).

"""
