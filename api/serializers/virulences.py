""" . """
from rest_framework import serializers
from virulence.models import Cluster, Ariba, AribaSequence


class VirulenceClusterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Cluster


class VirulenceAribaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ariba


class VirulenceAribaSequenceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = AribaSequence
