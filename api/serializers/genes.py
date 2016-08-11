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
        model = Clusters


class GeneFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features


class GeneProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product


class GeneInferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inference


class GeneNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note


class GeneBlastSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlastResults
