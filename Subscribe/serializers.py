from rest_framework import serializers
from .models import Subscribe_user
from .models import Subscribe_company


class SubscribeCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe_company
        fields = ['user', 'company']

    def create(self, validated_data):
        # 如果createtime不由Django自动生成，你可以在这里设置它
        # validated_data['createtime'] = ...
        return Subscribe_company.objects.create(**validated_data)

class SubscribeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe_user
        fields = ['user_src', 'user_dst']

    def create(self, validated_data):
        # 如果createtime不由Django自动生成，你可以在这里设置它
        # validated_data['createtime'] = ...
        return Subscribe_user.objects.create(**validated_data)