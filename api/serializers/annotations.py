""" . """
from rest_framework import serializers
from annotation.models import (
    Annotation,
    Repeat,
    Feature,
    Inference
)


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Annotation


class AnnotationRepeatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Repeat


class AnnotationFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Feature


class AnnotationInferenceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Inference
