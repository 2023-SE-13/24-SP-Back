from rest_framework import serializers
from CompanyManagement.models import CompanyMember
from .models import *


class UserSerializer(serializers.ModelSerializer):
    company_id = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'real_name', 'is_staff',
                  'education', 'desired_position', 'blog_link', 'repository_link', 'company_id', 'role', 'skills')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = [skill.name for skill in instance.skills.all()]
        return representation

    def get_company_id(self, obj):
        # 使用 filter() 替代 get() 并链式调用 first() 获取第一个匹配的实例
        company_member = CompanyMember.objects.filter(user=obj).first()
        return company_member.company.company_id if company_member else None

    def get_role(self, obj):
        company_member = CompanyMember.objects.filter(user=obj).first()
        return company_member.role if company_member else ""


class MessageSerializer(serializers.ModelSerializer):
    sender_uname = serializers.SerializerMethodField()
    receiver_uname = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['message_id', 'message_type', 'sender_uname', 'receiver_uname', 'content', 'timestamp']

    def get_sender_uname(self, obj):
        return obj.sender.username

    def get_receiver_uname(self, obj):
        return obj.receiver.username


class ConversationSerializer(serializers.ModelSerializer):
    user1_uname = serializers.SerializerMethodField()
    user2_uname = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'user1_uname', 'user2_uname', 'last_message_time']

    def get_user1_uname(self, obj):
        return obj.user1.username

    def get_user2_uname(self, obj):
        return obj.user2.username
