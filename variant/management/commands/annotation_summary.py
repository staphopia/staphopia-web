"""Give a per-annotation summary."""
from collections import OrderedDict

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from api.queries.variants import (
    get_annotated_snps_by_sample,
    get_annotated_indels_by_sample
)

from api.queries.tags import get_samples_by_tag
from api.queries.variants import get_variant_annotation
from api.utils import query_database


from sample.models import Sample
from staphopia.utils import jf_query
from variant.models import Reference, SNP


class Command(BaseCommand):
    """Give a per-annotation summary."""

    help = 'Give a per-annotation summary.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('tag', metavar='TAG',
                            help=('Tag to get samples.'))
        parser.add_argument('--reference', metavar='REFERENCE',
                            default='gi|29165615|ref|NC_002745.2|',
                            help=('Reference genome.'))
        parser.add_argument('--pass_only', action='store_true',
                            help='Only print annotation IDs that pass.')

    def handle(self, *args, **opts):
        """Give a per-annotation summary."""
        # Get User
        user = User.objects.get(username='ena')

        # Get Samples
        samples = get_samples_by_tag(opts['tag'], is_id=False)
        sample_id = [s['sample_id'] for s in samples]

        # Get Reference
        try:
            reference = Reference.objects.get(name=opts['reference'])
        except Reference.DoesNotExist:
            raise CommandError('Missing Reference: {0} == Exiting.'.format(
                opts['reference']
            ))

        # Get annotations
        annotations = {}
        for annotation in get_variant_annotation(None):
            annotations[annotation['id']] = annotation

        # Init annotation summary
        sql = """SELECT annotation_id
                 FROM variant_snp
                 WHERE is_genic=1
                 GROUP BY annotation_id
                 ORDER BY annotation_id;"""
        summary = OrderedDict()
        for row in query_database(sql):
            summary[row['annotation_id']] = {
                'snps': [],
                'indels': []
            }

        # Parse through variants for each sample
        sql = """SELECT v.sample_id, v.snp, v.indel
                 FROM variant_variant AS v
                 LEFT JOIN sample_basic AS s
                 ON v.sample_id=s.sample_id
                 WHERE v.sample_id IN ({0}) AND v.reference_id={1} AND
                       (s.is_public=TRUE OR s.user_id={2});""".format(
            ','.join([str(i) for i in sample_id]),
            reference.pk,
            user.pk
        )
        for row in query_database(sql):
            snps = {}
            for snp in row['snp']:
                snps[snp['annotation_id']] = True

            for annotation_id in snps:
                if annotation_id in summary:
                    summary[annotation_id]['snps'].append(row['sample_id'])

            indels = {}
            for indel in row['indel']:
                indels[indel['annotation_id']] = True

            for annotation_id in indels:
                if annotation_id in summary:
                    summary[annotation_id]['indels'].append(row['sample_id'])

        # Process the results
        cols = ['annotation_id', 'locus_tag', 'samples', 'snps', 'indels',
                'snp_all_samples', 'has_indel', 'annotation_pass']
        print('\t'.join(cols))
        for annotation_id, vals in summary.items():
            has_all = True if len(sample_id) == len(vals['snps']) else False
            has_indel = True if vals['indels'] else False
            is_good = True if has_all and not has_indel else False

            if opts['pass_only'] and not is_good:
                continue

            print('\t'.join([str(s) for s in [
                annotation_id,
                annotations[annotation_id]['locus_tag'],
                len(sample_id),
                len(vals['snps']),
                len(vals['indels']),
                has_all,
                has_indel,
                is_good
            ]]))
