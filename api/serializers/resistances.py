""" . """
from rest_framework import serializers
from resistance.models import Cluster, ResistanceClass, Ariba, AribaSequence


class ResistanceClusterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Cluster


class ResistanceClassSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ResistanceClass


class ResistanceAribaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ariba


class ResistanceAribaSequenceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = AribaSequence
