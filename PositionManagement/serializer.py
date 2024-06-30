from rest_framework import serializers

from PositionManagement.models import Position, Application


class PositionSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', read_only=True)
    application_count = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    class Meta:
        model = Position
        fields = '__all__'

    def to_representation(self, instance):
        skills = instance.skill_required.all()
        skill_names = [skill.name for skill in skills]
        representation = super().to_representation(instance)
        representation['company_id'] = representation.pop('company')
        representation['skill_required'] = skill_names
        return representation

    def get_application_count(self, obj):
        # 计算每个职位的申请数量
        return Application.objects.filter(position=obj).count()
    
    def get_company_name(self, obj):
        return obj.company.company_name
