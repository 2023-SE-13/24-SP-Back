from rest_framework import serializers

from CompanyManagement.models import CompanyMember
from .models import *


class TweetSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    comment_array = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    is_like = serializers.SerializerMethodField()
 
    class Meta:
        model = Tweet
        fields = ('tweet_id', 'user', 'text_content', 'created_at', 'likes', 'is_like', 'comments', 'photos', 'comment_array')
    def get_photos(self, obj):
        tweet_photos = TweetPhoto.objects.filter(tweet=obj)
        photos = []
        for tweet_photo in tweet_photos:
            photos.append(
                os.path.basename(tweet_photo.photo.name)
            )
        return photos
    
    def get_user(self, obj):
        return obj.user.username if obj else None
    
    def get_comment_array(self, obj):
        comments = Comment.objects.filter(tweet=obj).order_by('-created_at')
        comment_array = []
        for comment in comments:
            if comment.target_comment is None:
                comment_array.append(comment.comment_id)
        return comment_array
    
    def get_is_like(self, obj):
        if Likes.objects.filter(tweet=obj, user=obj.user).exists():
            return True
        else:
            return False