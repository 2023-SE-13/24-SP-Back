from rest_framework import serializers

from PositionManagement.models import Position


class PositionSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', read_only=True)

    class Meta:
        model = Position
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company_id'] = representation.pop('company')
        return representation
