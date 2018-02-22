""" . """
from rest_framework import serializers
from variant.models import (
    SNP,
    Indel,
    Annotation,
    Comment,
    Feature,
    Filter,
    Reference,
    Variant
)


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Variant


class SNPSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = SNP


class InDelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Indel


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Annotation


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Comment


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Filter


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Feature


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Reference
