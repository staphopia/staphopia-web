""" . """
from rest_framework import serializers
from kmer.models import Total


class KmerTotalSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Total
