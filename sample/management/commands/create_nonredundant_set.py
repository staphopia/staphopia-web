""" Create a non-redundant set of Samples based on seqeunce type. """
from collections import OrderedDict
import datetime
import random

from django.db import transaction
from django.core.management.base import BaseCommand

from api.utils import query_database

from tag.models import ToSample
from sample.models import Sample
from sample.tools import create_tag, get_user


class Command(BaseCommand):

    """ Create new sample for custom sample. """

    help = 'Create new sample for custom data.'

    def add_arguments(self, parser):
        parser.add_argument('tag', metavar='TAG',
                            help=('Tag name.'))
        parser.add_argument(
            '--rank', type=str, default="1",
            help=('Limit set to at least rank (Default: 1 (Bronze))')
        )
        parser.add_argument('--published', action='store_true',
                            help='Limit set to published only.')
        parser.add_argument('--singletons', action='store_true',
                            help='Include STs represented by a single sample.')
        parser.add_argument('--limit', type=int, default=0,
                            help='Limit number of samples (Default: All).')

    def get_sample(self, samples, singletons):
        if len(samples) > 1:
            random.seed(123456789)
            return random.choice(samples)
        elif singletons:
            return samples[0]
        else:
            return None

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Create new sample for custom sample. """
        # Required Parameters
        user = get_user('ena')

        # Get Samples
        sql = """SELECT s.sample_id, name, st, rank,
                        metadata->'isolation_source' AS isolation_source,
                        metadata->'location' AS location,
                        metadata->'collection_date' AS collection_date
                 FROM sample_basic AS s
                 LEFT JOIN sample_metadata AS m
                 ON s.sample_id=m.sample_id
                 LEFT JOIN variant_variant AS v
                 ON s.sample_id=v.sample_id
                 WHERE user_id={0} and st>0 and rank>={1} AND
                       v.snp_count <= 60000 {2}
                 ORDER BY st
                 {3};""".format(
            user.pk,
            opts['rank'],
            'AND is_published=True' if opts['published'] else '',
            f"LIMIT {opts['limit']}" if opts['limit'] else ''
        )
        sequence_types = OrderedDict()
        total_samples = 0
        for sample in query_database(sql):
            if sample['st'] not in sequence_types:
                sequence_types[sample['st']] = {
                    'all_fields': [],
                    'two_fields': [],
                    'one_field': [],
                    'missing_metadata': [],
                    'total': 0
                }
            has_location = ("unknown" not in sample['location'] and
                            sample['location'] != "not collected")
            has_date = True if sample['collection_date'] else False
            has_source = True if sample['isolation_source'] else False

            if has_location and has_source and has_date:
                sequence_types[sample['st']]['all_fields'].append(sample)
            elif has_location and has_source:
                sequence_types[sample['st']]['two_fields'].append(sample)
            elif has_location and has_date:
                sequence_types[sample['st']]['two_fields'].append(sample)
            elif has_source and has_date:
                sequence_types[sample['st']]['two_fields'].append(sample)
            elif has_location or has_source or has_date:
                sequence_types[sample['st']]['one_field'].append(sample)
            else:
                sequence_types[sample['st']]['missing_metadata'].append(sample)

            sequence_types[sample['st']]['total'] += 1
            total_samples += 1

        with open('non-redundant-set.txt', 'w') as fh:
            cols = ['st', 'choice', 'total', 'all_fields', 'two_fields',
                    'one_field', 'missing_metadata', 'sample_id', 'name',
                    'isolation_source', 'location', 'collection_date']
            fh.write('\t'.join(cols))
            fh.write('\n')
            total = {'all_fields': 0, 'two_fields': 0, 'one_field': 0,
                     'missing_metadata': 0, 'total': 0,
                     'total_samples': total_samples}

            samples_to_tag = []
            for sequence_type, samples in sequence_types.items():
                sample = None
                choice = None
                if samples['all_fields']:
                    sample = self.get_sample(samples['all_fields'],
                                             opts['singletons'])
                    choice = 'all_fields'
                    total['all_fields'] += 1
                elif samples['two_fields']:
                    sample = self.get_sample(samples['two_fields'],
                                             opts['singletons'])
                    total['two_fields'] += 1
                    choice = 'two_fields'
                elif samples['one_field']:
                    sample = self.get_sample(samples['one_field'],
                                             opts['singletons'])
                    total['one_field'] += 1
                    choice = 'one_field'
                elif samples['missing_metadata']:
                    sample = self.get_sample(samples['missing_metadata'],
                                             opts['singletons'])
                    total['missing_metadata'] += 1
                    choice = 'missing_metadata'

                if sample:
                    fields = [
                        sequence_type, choice, samples["total"],
                        len(samples["all_fields"]), len(samples["two_fields"]),
                        len(samples["one_field"]),
                        len(samples["missing_metadata"]), sample['sample_id'],
                        sample['name'], sample['isolation_source'],
                        sample['location'], sample['collection_date']
                    ]
                    fh.write('\t'.join([str(f) for f in fields]))
                    fh.write('\n')
                    samples_to_tag.append(sample['sample_id'])
                    total['total'] += 1

        # Create Tag
        comment = (
            "A set of {0} STs represented by a single sample associated with "
            "a publication and Gold ranked. For sequence types represented "
            "by multiple samples, a random sample was selected. Priority of "
            "selection was given to samples in which the source of "
            "isolation, location of collection and date of collection were "
            "known. This set of {0} STs is derived from {1} samples in all, "
            "{2} STs are represented by a sample with each field filled, "
            "{3} STs are represented by a sample with two fields filled, "
            "{4} STs are represented by a sample with a single field filled, "
            "{5} STs are represented by a sample without any fields filled. "
            "Created on {6}."
        ).format(
            total['total'],
            total['total_samples'],
            total['all_fields'],
            total['two_fields'],
            total['one_field'],
            total['missing_metadata'],
            datetime.date.today().strftime("%B %d, %Y")
        )

        tag = create_tag(user, opts['tag'], comment)
        for sample_id in samples_to_tag:
            sample = Sample.objects.get(pk=sample_id)
            ToSample.objects.get_or_create(sample=sample, tag=tag)

        print(f'Created Tag: {tag.tag}')
        print(f'Tag Comment: {tag.comment}')
