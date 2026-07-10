from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required.')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_verified', False)
        extra_fields.setdefault('role', User.Role.CREATOR)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        CREATOR = 'creator', 'Creator'
        ADMIN = 'admin', 'Admin'

    username = None
    email = models.EmailField('email address', unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    stage_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    genres = models.JSONField(default=list, blank=True)
    profile_photo = models.FileField(upload_to='profile_photos/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CREATOR)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
