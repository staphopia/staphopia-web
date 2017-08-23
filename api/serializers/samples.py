""" . """
from rest_framework import serializers
from sample.models import (
    Sample,
    Publication,
    Tag,
    ToTag,
    Resistance,
    ToResistance
)


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Sample


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class ToTagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ToTag


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Publication


class ResistanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Resistance


class ToResistanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ToResistance
