""" . """
from rest_framework import serializers
from assembly.models import Stats, Contigs


class AssemblyStatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Stats


class ContigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contigs
        fields = ('id', 'is_plasmids', 'name', 'sample')


class ContigFullSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Contigs
