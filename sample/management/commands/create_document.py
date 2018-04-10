"""For all samples, create a document for full text searches."""

from django.db import transaction, connection
from django.core.management.base import BaseCommand


from api.queries.genes import get_genes_by_sample
from api.queries.resistances import get_ariba_resistance
from api.queries.virulences import get_ariba_virulence
from api.utils import query_database


class Command(BaseCommand):
    """For all samples, create a document for full text searches."""

    help = 'For all samples, create a document for full text searches.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--debug', action='store_true',
                            help=('Create document for a single sample.'))

    def handle(self, *args, **opts):
        """For all samples, create a document for full text searches."""
        rank = {1: 'Bronze', 2: 'Silver', 3: 'Gold'}
        sql = """SELECT s.sample_id, user_id, name, rank, st, metadata
                 FROM sample_basic AS s
                 LEFT JOIN sample_metadata as m
                 ON s.sample_id=m.sample_id
                 WHERE s.user_id=2
                 ORDER BY s.sample_id;"""
        for sample in query_database(sql):
            document = []
            for key in sample['metadata']:
                val = sample['metadata'][key]
                if str(val).lower() not in ['true', 'false', '1280',
                                            'unknown/missing']:
                    document.append(val)
            document.append(f"ST{sample['st']}")
            document.append(rank[sample['rank']])
            document.append(sample['name'])

            # Get information pertaining to predicted genes
            for row in get_genes_by_sample([sample['sample_id']],
                                           sample['user_id']):
                for word in row['inference'].split():
                    document.append(word)
                for word in row['product'].split():
                    document.append(word)
                for word in row['name'].split():
                    document.append(word)
                for word in row['note'].split():
                    document.append(word)

            # Resistance
            for row in get_ariba_resistance([sample['sample_id']],
                                            sample['user_id']):
                for word in row['cluster'].split():
                    document.append(word)
                for word in row['resistance_class'].split():
                    document.append(word)
                for word in row['mechanism'].split():
                    document.append(word)

            # Virulence
            for row in get_ariba_virulence([sample['sample_id']],
                                           sample['user_id']):
                document.append(row['cluster_name'])

            results = []
            for row in get_ariba_resistance([sample['sample_id']],
                                            sample['user_id'], mec_only=True):
                results.append(row)
            if results:
                document.append('MRSA')
            else:
                document.append('MSSA')
            # genes = self.get_genes(sample.id)
            print(f"Working on {sample['name']} ({sample['sample_id']})")
            final_set = []
            for word in list(set(document)):
                try:
                    int(word)
                except ValueError:
                    final_set.append(word)
            final_set = " ".join(sorted(final_set))
            if opts['debug']:
                print(final_set)
                break
            else:
                self.update_table(final_set, row['sample_id'])

    @transaction.atomic
    def update_table(self, document, sample_id):
        with connection.cursor() as cursor:
            sql = """UPDATE sample_metadata
                     SET document=to_tsvector('english', %s)
                     WHERE sample_id=%s"""
            cursor.execute(sql, (document, sample_id))
