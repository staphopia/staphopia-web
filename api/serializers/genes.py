""" . """
from rest_framework import serializers
from gene.models import (
    Clusters,
    Features,
    Product,
    Inference,
    Note,
    BlastResults
)


class GeneClusterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Clusters


class GeneFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Features


class GeneProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Product


class GeneInferenceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Inference


class GeneNoteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Note


class GeneBlastSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = BlastResults
