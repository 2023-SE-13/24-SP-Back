from rest_framework import serializers

from PositionManagement.models import Position


class PositionSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', read_only=True)

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
