from rest_framework import serializers

from CompanyManagement.models import CompanyMember
from .models import *


class UserSerializer(serializers.ModelSerializer):
    company_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'real_name', 'is_staff',
                  'education', 'desired_position', 'blog_link', 'repository_link', 'company_id')

    def get_company_id(self, obj):
        # 使用 filter() 替代 get() 并链式调用 first() 获取第一个匹配的实例
        company_member = CompanyMember.objects.filter(user=obj).first()
        return company_member.company.company_id if company_member else None

