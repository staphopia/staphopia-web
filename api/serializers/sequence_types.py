""" . """
from rest_framework import serializers
from mlst.models import Blast, Srst2


class BlastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blast


class Srst2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Srst2
