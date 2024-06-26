from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'real_name', 'is_staff',
                  'education', 'desired_position', 'blog_link', 'repository_link')
