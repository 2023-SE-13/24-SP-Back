from django.contrib.auth.models import AbstractUser
from django.db import models

from UserManagement.models import User
# User model, extending Django's AbstractUser
from shared.utils.datetime import get_expiry_time


class Company(models.Model):
    company_id = models.CharField(max_length=40, primary_key=True, auto_created=True)
    company_name = models.CharField(max_length=255)
    company_description = models.CharField(max_length=255)
    company_image = models.ImageField(upload_to='resources/company_images/', null=True, blank=True)

    class Meta:
        db_table = 'Companys'

    def __str__(self):
        return self.company_name


class CompanyMember(models.Model):
    ROLE_TYPE_CHOICES = [
        ('Creator', 'Creator'),
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=255,
        choices=ROLE_TYPE_CHOICES,
        default='Staff',
    )

    class Meta:
        db_table = 'CompanyMembers'
        unique_together = ['company', 'user']  # 确保每个组合的(company, user)是唯一的

    def __str__(self):
        return f"{self.company} - {self.user} ({self.get_role_display()})"


class JoinVerification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)