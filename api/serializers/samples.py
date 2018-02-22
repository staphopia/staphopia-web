""" . """
from rest_framework import serializers
from sample.models import Sample, Metadata


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Sample


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Metadata
