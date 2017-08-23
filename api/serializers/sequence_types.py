""" . """
from rest_framework import serializers
from mlst.models import Blast, Srst2


class BlastSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Blast


class Srst2Serializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Srst2
