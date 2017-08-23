""" . """
from rest_framework import serializers
from ena.models import Study, Experiment, Run


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Study


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Experiment


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Run
