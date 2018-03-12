""" . """
from rest_framework import serializers
from mlst.models import MLST
from cgmlst.models import CGMLST


class MLSTSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MLST

class CGMLSTSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CGMLST
