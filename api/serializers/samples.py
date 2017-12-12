""" . """
from rest_framework import serializers
from sample.models import Sample


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Sample
