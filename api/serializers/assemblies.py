""" . """
from rest_framework import serializers
from assembly.models import Summary, Contig


class AssemblyStatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Summary


class ContigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contig
        fields = ('id', 'name', 'sample')


class ContigFullSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Contig
