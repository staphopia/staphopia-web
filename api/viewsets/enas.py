from collections import OrderedDict
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework import viewsets
from rest_framework.decorators import detail_route

from api.pagination import CustomReadOnlyModelViewSet
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


class EnaExperimentViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ENA Experiments."""
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = ()
    queryset = ''
    serializer_class = ExperimentSerializer

    @detail_route(methods=['get'])
    def info(self, request, pk=None):
        try:
            exp = Experiment.objects.get(experiment_accession=pk)
            client = APIClient()
            client.force_authenticate(user=User.objects.get(username='test'))

            run_info = []
            is_miseq = True if 'miseq' in exp.instrument_model.lower() else False
            runs = Run.objects.filter(experiment_accession=pk)
            if runs.count() > 0:
                for run in runs:
                    run_info.append(OrderedDict((
                        ('run', run.run_accession),
                        ('is_paired', run.is_paired),
                        ('is_miseq', is_miseq),
                        ('ftp', filter(None, run.fastq_ftp.split(';'))),
                        ('aspera', filter(None, run.fastq_aspera.split(';'))),
                        ('md5', filter(None, run.fastq_md5.split(';')))
                    )))

            return self.formatted_response(run_info)
        except Experiment.DoesNotExist:
            return self.formatted_response([])


class EnaRunViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ENA Runs."""

    queryset = Run.objects.all()
    serializer_class = RunSerializer
