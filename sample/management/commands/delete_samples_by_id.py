"""Delete all samples associated with a Sample ID."""
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from sample.models import (
    ToTag, Sample, ToResistance, ToPublication, EnaMetaData
)

from assembly.models import Stats, Contigs
from gene.models import Features, BlastResults
from kmer.models import Total
from mlst.models import Blast, Srst2
from sccmec.models import Coverage, Primers, Proteins
from sequence.models import Stat
from variant.models import ToIndel, ToSNP, Counts


class Command(BaseCommand):
    """Delete all samples associated with a Sample ID."""

    help = 'Delete all samples associated with a Sample ID.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample', type=str, default="",
                            help='Sample to delete.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Delete sample associated with an ID."""
        try:
            sample = Sample.objects.get(pk=opts['sample'])
        except Sample.DoesNotExist:
            raise CommandError('Sample: {0} does not exist'.format(
                opts['sample']
            ))

        analysis_models = [
            Stats, Contigs, Features, BlastResults, Total, Blast, Srst2,
            Coverage, Primers, Proteins, Stat, ToIndel, ToSNP, Counts
        ]
        sample_models = [ToTag, ToResistance, ToPublication, EnaMetaData]
        print('Working on {0}...'.format(sample.sample_tag))
        self.delete_rows(analysis_models, sample)
        self.delete_rows(sample_models, sample)
        print('\tDeleting Sample {0}'.format(sample.sample_tag))
        sample.delete()

    @transaction.atomic
    def delete_rows(self, models, sample):
        """Delete all rows from amodel associated with a sample."""
        for model in models:
            print('\tDeleteing rows from {0} associated with {1}'.format(
                model.__name__, sample.sample_tag
            ))
            model.objects.filter(sample=sample).delete()
