from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

from users.models import User
from users.serializers import UserSerializer

import random

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', None)
        email = request.data.get('email', None)
        password = request.data.get('password')

        user = None
        if phone_number:
            user = authenticate(phone_number=phone_number, password=password)
        elif email:
            user = authenticate(email=email, password=password)

        if user is not None and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    Handles password reset via email or OTP to phone number.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', None)
        email = request.data.get('email', None)

        user = None
        if phone_number:
            user = get_object_or_404(User, phone_number=phone_number)
        elif email:
            user = get_object_or_404(User, email=email)
        else:
            return Response({"error": "Provide either email or phone number"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = random.randint(100000, 999999)
        user.set_password(str(otp))  # Temporarily setting OTP as password (should be replaced later)
        user.save()

        if email:
            send_mail(
                "Password Reset OTP",
                f"Your password reset OTP is: {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to registered email"}, status=status.HTTP_200_OK)
        
        if phone_number:
            # You can replace this with an SMS service like Twilio later
            print(f"Send this OTP to phone {phone_number}: {otp}")
            return Response({"message": "OTP sent to registered phone number"}, status=status.HTTP_200_OK)

        return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    """
    Resets password after OTP verification.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', None)
        email = request.data.get('email', None)
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        user = None
        if phone_number:
            user = get_object_or_404(User, phone_number=phone_number)
        elif email:
            user = get_object_or_404(User, email=email)
        else:
            return Response({"error": "Provide either email or phone number"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp or not new_password:
            return Response({"error": "OTP and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(str(otp)):  # Verify OTP
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
