""" . """
from rest_framework import serializers
from mlst.models import MLST


class MLSTSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MLST

