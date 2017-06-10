"""Delete all samples associated with a Tag."""
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from sample.models import ToTag, Tag, ToResistance, ToPublication

from assembly.models import Stats, Contigs
from gene.models import Features, BlastResults
from kmer.models import Total
from mlst.models import Blast, Srst2
from sccmec.models import Coverage, Primers, Proteins
from sequence.models import Stat
from variant.models import ToIndel, ToSNP, Counts


class Command(BaseCommand):
    """Delete all samples associated with a Tag."""

    help = 'Delete all samples associated with a Tag.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('tag', type=str, default="",
                            help='Tag to delete associated samples.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Delete all samples associated with a tag."""
        try:
            tag = Tag.objects.get(tag=opts['tag'])
        except Tag.DoesNotExist:
            raise CommandError('Tag: {0} does not exist'.format(
                opts['tag']
            ))

        analysis_models = [
            Stats, Contigs, Features, BlastResults, Total, Blast, Srst2,
            Coverage, Primers, Proteins, Stat, ToIndel, ToSNP,
            Counts
        ]
        sample_models = [ToTag, ToResistance, ToPublication]

        hits = ToTag.objects.filter(tag=tag)
        for hit in hits:
            print('Working on {0}...'.format(hit.sample.sample_tag))
            self.delete_rows(analysis_models, hit.sample)
            self.delete_rows(sample_models, hit.sample)
            print('\tDeleting Sample {0}'.format(hit.sample.sample_tag))
            hit.sample.delete()

    @transaction.atomic
    def delete_rows(self, models, sample):
        """Delete all rows from amodel associated with a sample."""
        for model in models:
            print('\tDeleteing rows from {0} associated with {1}'.format(
                model.__name__, sample.sample_tag
            ))
            model.objects.filter(sample=sample).delete()
