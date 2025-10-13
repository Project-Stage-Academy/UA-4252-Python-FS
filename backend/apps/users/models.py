from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import uuid


class User(AbstractUser):
    """Custom Django User model without username"""
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
