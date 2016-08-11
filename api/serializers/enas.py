""" . """
from rest_framework import serializers
from ena.models import Study, Experiment, Run


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
