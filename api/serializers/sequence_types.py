""" . """
from rest_framework import serializers
from mlst.models import Blast


class BlastSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Blast
