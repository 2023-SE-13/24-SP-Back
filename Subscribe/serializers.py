from rest_framework import serializers
from .models import SubscribeUser
from .models import SubscribeCompany


class SubscribeCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeCompany
        fields = ['user', 'company']

    def create(self, validated_data):
        # 如果createtime不由Django自动生成，你可以在这里设置它
        # validated_data['createtime'] = ...
        return SubscribeCompany.objects.create(**validated_data)

class SubscribeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeUser
        fields = ['user_src', 'user_dst']

    def create(self, validated_data):
        # 如果createtime不由Django自动生成，你可以在这里设置它
        # validated_data['createtime'] = ...
        return SubscribeUser.objects.create(**validated_data)