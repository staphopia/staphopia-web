"""For all samples, create a document for full text searches."""

from django.db import transaction, connection
from django.core.management.base import BaseCommand


from api.utils import query_database
from sample.models import Sample


class Command(BaseCommand):
    """For all samples, create a document for full text searches."""

    help = 'For all samples, create a document for full text searches.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--debug', action='store_true',
                            help=('Create document for a single sample.'))

    def handle(self, *args, **opts):
        """For all samples, create a document for full text searches."""
        for sample in Sample.objects.all().order_by('user_id'):
            rank = self.get_rank(sample.id)
            metadata = self.get_metadata(sample.id)
            st = self.get_sequence_type(sample.id)
            # genes = self.get_genes(sample.id)
            print("Working on {0} ({1})".format(sample.sample_tag, sample.id))
            if opts['debug']:
                print(" ".join([sample.sample_tag, rank, metadata, st]))
                break
            else:
                document = " ".join(
                    [sample.sample_tag, rank, metadata, st]
                )
                self.update_table(document, sample.id)

    @transaction.atomic
    def update_table(self, document, sample_id):
        with connection.cursor() as cursor:
            sql = """UPDATE sample_sample
                     SET document=to_tsvector('english', %s)
                     WHERE id=%s"""
            cursor.execute(sql, (document, sample_id))

    def create_string(self, sql):
        rows = query_database(sql)
        text = []
        for row in rows:
            text.append(" ".join(row.values()))
        return " ".join(text)

    def get_rank(self, sample_id):
        rank = {1: 'Bronze', 2: 'Silver', 3: 'Gold'}
        sql = """SELECT rank FROM sequence_stat
                 WHERE is_original=FALSE AND sample_id={0}""".format(sample_id)
        row = query_database(sql)[0]
        return rank[row['rank']]

    def get_metadata(self, sample_id):
        """Retrieve metadata associated with a sample."""
        cols = [
            'study_accession', 'study_title',
            'secondary_study_accession', 'sample_accession',
            'secondary_sample_accession', 'submission_accession',
            'experiment_accession', 'experiment_title',
            'scientific_name', 'instrument_platform', 'instrument_model',
            'center_name', 'center_link', 'cell_line', 'collected_by',
            'country', 'description', 'environmental_sample', 'germline',
            'isolate', 'isolation_source', 'location', 'country', 'region',
            'coordinates', 'serotype', 'serovar', 'sex', 'submitted_sex',
            'strain', 'sub_species', 'tissue_type',
            'biosample_scientific_name',
            'biosample_center_name', 'environment_biome',
            'environment_feature', 'environment_material', 'project_name',
            'host', 'host_status', 'host_sex',
            'submitted_host_sex', 'host_body_site', 'investigation_type',
            'sequencing_method', 'broker_name',
        ]
        sql = """SELECT {0} FROM sample_metadata
                 WHERE sample_id={1};""".format(
            ",".join(cols), sample_id
        )
        return self.create_string(sql)

    def get_sequence_type(self, sample_id):
        """Retrieve sequence type for a sample."""
        sql = """SELECT 'ST'||st_stripped as st_stripped
                 FROM mlst_srst2
                 WHERE sample_id={0};""".format(
            sample_id
        )
        return self.create_string(sql)

    def get_genes(self, sample_id):
        sql = """SELECT c.name, p.product, n.note
                 FROM gene_features AS f
                 LEFT JOIN gene_clusters AS c
                 ON f.cluster_id=c.id
                 LEFT JOIN gene_product AS p
                 ON f.product_id=p.id
                 LEFT JOIN gene_note AS n
                 ON f.note_id=n.id
                 WHERE f.sample_id={0}""".format(sample_id)
        return self.create_string(sql)
