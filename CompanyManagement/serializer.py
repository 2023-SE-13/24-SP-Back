# CompanyManage/serializers.py

from rest_framework import serializers

from UserManagement.serializers import UserSerializer
from .models import *


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class CompanyMemberUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # 嵌套使用 UserSerializer
    role = serializers.CharField()  # 显式声明，以便将其包括在序列化输出中

    class Meta:
        model = CompanyMember
        fields = ('user', 'role')  # 返回 'user' 和 'role'


class CompanyMemberCompanySerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    role = serializers.CharField()

    class Meta:
        model = CompanyMember
        fields = ('company', 'role')