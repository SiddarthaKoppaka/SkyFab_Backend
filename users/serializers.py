from rest_framework import serializers
from users.models import User, UserProfile
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = UserProfile
        fields = ('title', 'date_of_birth', 'address', 'country', 'city', 'zip', 'photo')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for User model with phone authentication"""
    phone_number = PhoneNumberField(region="IN", required=True)
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('url', 'phone_number', 'email', 'first_name', 'last_name', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone_number(self, value):
        """Ensure phone number is in the correct +91 format"""
        if not str(value).startswith("+91"):
            raise serializers.ValidationError("Phone number must be an Indian number starting with +91.")
        return value

    def create(self, validated_data):
        """Create user and profile"""
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        with transaction.atomic():
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
