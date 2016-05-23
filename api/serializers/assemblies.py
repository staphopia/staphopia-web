""" . """
from rest_framework import serializers
from assembly.models import Stats, Contigs


class AssemblyStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats


class ContigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contigs
