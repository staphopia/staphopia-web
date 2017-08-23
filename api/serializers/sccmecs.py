""" . """
from rest_framework import serializers
from sccmec.models import Cassette, Coverage, Primers, Proteins


class SCCmecCassetteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Cassette


class SCCmecCoverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coverage
        fields = ('id', 'total', 'minimum', 'mean', 'median', 'maximum',
                  'meca_total', 'meca_minimum', 'meca_mean', 'meca_median',
                  'meca_maximum', 'cassette',  'sample')


class SCCmecPrimerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Primers


class SCCmecProteinSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Proteins
