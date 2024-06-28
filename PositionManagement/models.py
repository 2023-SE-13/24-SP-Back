import uuid

from django.db import models

# Create your models here.
from CompanyManagement.models import Company
from UserManagement.models import User


class Position(models.Model):
    position_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False, default=uuid.uuid4)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position_name = models.CharField(max_length=255)
    position_description = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    education_requirement = models.CharField(max_length=255, null=True, blank=True)
    salary = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'Positions'

    def __str__(self):
        return self.position_name


class Application(models.Model):
    application_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False,
                                      default=uuid.uuid4)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'applications'

    def __str__(self):
        return f"Application by {self.user.username} for {self.position.position_name}"