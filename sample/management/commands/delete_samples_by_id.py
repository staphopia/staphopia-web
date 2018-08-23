"""Delete all samples associated with a Sample ID."""
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from sample.models import (
    Sample, Metadata
)

from assembly.models import Contig, Sequence, Summary
from cgmlst.models import CGMLST, Report as CGMLSTreport
from gene.models import Features, BlastResults
from mlst.models import MLST, Report as MLSTreport
from plasmid.models import (
    Contig as PlasmidContig,
    Sequence as PlasmidSequence,
    Summary as PlasmidSummary
)
from resistance.models import Ariba, AribaSequence
from sccmec.models import Coverage, Primers, Proteins, Subtypes
from sequence.models import Summary as SequenceSummary
from variant.models import Variant
from virulence.models import (
    Ariba as VirulenceAriba, AribaSequence as VirulenceSequence
)


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
            Contig, Sequence, Summary, Features, BlastResults,
            CGMLSTreport, CGMLST, MLSTreport, MLST, PlasmidSummary,
            PlasmidSequence, PlasmidContig, Subtypes, Coverage, Primers,
            Proteins, Ariba, AribaSequence, SequenceSummary, Variant,
            VirulenceAriba, VirulenceSequence
        ]
        sample_models = [Metadata]
        print('Working on {0}...'.format(sample.name))
        self.delete_rows(analysis_models, sample)
        self.delete_rows(sample_models, sample)
        print('\tDeleting Sample {0}'.format(sample.name))
        sample.delete()

    @transaction.atomic
    def delete_rows(self, models, sample):
        """Delete all rows from amodel associated with a sample."""
        for model in models:
            print('\tDeleteing rows from {0} associated with {1}'.format(
                model.__name__, sample.name
            ))
            model.objects.filter(sample=sample).delete()
