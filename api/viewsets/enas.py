from rest_framework import viewsets

from api.serializers.enas import (
    StudySerializer,
    ExperimentSerializer,
    RunSerializer
)
from ena.models import Study, Experiment, Run


class EnaStudyViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ENA Samples."""

    queryset = Study.objects.all()
    serializer_class = StudySerializer


class EnaExperimentViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ENA Experiments."""

    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer


class EnaRunViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ENA Runs."""

    queryset = Run.objects.all()
    serializer_class = RunSerializer
