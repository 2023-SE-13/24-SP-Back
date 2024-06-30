import uuid

from django.db import models

from CompanyManagement.models import Company
from TweetManagement.models import Tweet
from UserManagement.models import User, Message


# Create your models here.
class Notification(models.Model):
    TYPE_CHOICES = (
        ('message', 'Message Mention'),
        ('subscribe', 'Subscribe Mention'),
        ('system', 'System Notification')
    )
    notification_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)
    tweet = models.ForeignKey(Tweet, related_name='notifications', on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, related_name='notifications', on_delete=models.CASCADE, null=True)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE, null=True)