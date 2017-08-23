""" . """
from rest_framework import serializers
from sequence.models import Stat


class SequenceStatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Stat
