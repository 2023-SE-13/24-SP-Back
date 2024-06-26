from django.contrib.auth.models import AbstractUser
from django.db import models
from UserManagement.models import User
from CompanyManagement.models import Company
# Create your models here.


class Subscribe_company(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # 在Django的admin中显示这个模型时，你可以定义更友好的显示名
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

        # 可以添加其他方法，比如字符串表示方法

    def __str__(self):
        return f"{self.user} subscribes to {self.company}"


class Subscribe_user(models.Model):
    user_dst = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribe_user_dst_set')
    user_src = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribe_user_src_set')
    created_at = models.DateTimeField(auto_now_add=True)

    # 在Django的admin中显示这个模型时，你可以定义更友好的显示名
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

        # 可以添加其他方法，比如字符串表示方法

    def __str__(self):
        return f"{self.user_src} subscribes to {self.user_dst}"