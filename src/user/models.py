from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if not username:
            raise ValueError("Login is required :)")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractUser, PermissionsMixin):
    class Role(models.TextChoices):
        admin = 'admin'
        creator = 'creator'
        sale = 'sale'

    email = models.EmailField(unique=True)
    # username = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True, auto_now=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['created_at']


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    username = models.CharField(max_length=150)
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    fullname = models.CharField(max_length=150)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.fullname}'
