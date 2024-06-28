from rest_framework import serializers

from CompanyManagement.models import CompanyMember
from .models import *


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ('tweet_id', 'user', 'content', 'created_at', 'updated_at')