""" . """
from rest_framework import serializers
from sequence.models import Summary


class SequenceStatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Summary
