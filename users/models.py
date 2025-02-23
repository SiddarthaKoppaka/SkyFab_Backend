from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(BaseUserManager):
    """Custom user model manager where authentication is based on phone number or email"""

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone number is required'))
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Custom User model using phone number as primary authentication"""
    username = None
    phone_number = PhoneNumberField(
    unique=True,  # Reapply unique constraint
    region="IN",
    verbose_name=_('phone number'),
    help_text=_('Indian phone number (+91) required')
)


    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=True, 
        null=True,
        help_text=_('Used as an alternative contact or recovery option')
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return str(self.phone_number)


class UserProfile(models.Model):
    """Extended User Profile"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    title = models.CharField(
        max_length=5,
        blank=True, 
        null=True
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True
    )
    address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True
    )
    country = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    city = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    zip = models.CharField(
        max_length=10, 
        blank=True, 
        null=True
    )
    photo = models.ImageField(
        upload_to='uploads/', 
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"Profile of {self.user.phone_number}"
