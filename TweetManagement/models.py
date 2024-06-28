import uuid

from django.db import models

from UserManagement.models import User


# Create your models here.

class Tweet(models.Model):
    tweet_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        db_table = 'Tweets'

    def __str__(self):
        return f"{self.user} - {self.tweet_id}"

class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False, default=uuid.uuid4)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Comments'

    def __str__(self):
        return f"{self.user} - {self.comment_id} ({self.tweet})"