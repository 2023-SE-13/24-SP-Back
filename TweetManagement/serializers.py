from rest_framework import serializers

from CompanyManagement.models import CompanyMember
from .models import *


class TweetSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    comment_tree = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
 
    class Meta:
        model = Tweet
        fields = ('tweet_id', 'user', 'text_content', 'created_at', 'likes', 'comments', 'photos', 'comment_tree')
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
    
    def get_comment_tree(self, obj):
        comments = Comment.objects.filter(tweet=obj)
        comment_tree = []
        for comment in comments:
            if comment.target_comment:
                comment_tree[comment.target_comment.comment_id].append(comment.comment_id)
            else:
                comment_tree.append([comment.comment_id])
        return comment_tree if comment_tree else None