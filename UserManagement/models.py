from django.contrib.auth.models import AbstractUser
from django.db import models
from shared.utils.datetime import get_expiry_time


class Skill(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'Skills'

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, primary_key=True)
    real_name = models.CharField(max_length=255)
    education = models.CharField(max_length=255, null=True)
    desired_position = models.CharField(max_length=255, null=True)
    blog_link = models.CharField(max_length=255, null=True)
    repository_link = models.CharField(max_length=255, null=True)
    user_subscription = models.IntegerField(default=0)
    resume = models.FileField(upload_to='resources/resumes/', null=True, blank=True)
    desired_work_city = models.CharField(max_length=255, null=True)  # 新添加的字段：意向工作城市
    skills = models.ManyToManyField(Skill, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 最低薪资
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 最高薪资

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






