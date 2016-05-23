""" . """
from rest_framework import serializers
from variant.models import (
    SNP,
    Indel,
    Annotation,
    Comment,
    Confidence,
    Feature,
    Filter,
    Reference
)


class SNPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SNP

class InDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indel

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment

class ConfidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Confidence

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
