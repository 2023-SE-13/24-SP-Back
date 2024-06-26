from django.contrib.auth.models import AbstractUser
from django.db import models
from shared.utils.datetime import get_expiry_time


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, primary_key=True)
    real_name = models.CharField(max_length=255)
    user_subscription = models.IntegerField(default=0)
    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiry_time)

    def __str__(self):
        return self.email



