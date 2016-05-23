"""
Kmer Application Models.

These are models to store information on the Kmer analysis of Staphopia
samples.
"""
import architect
import time

from django.db import models, connection, transaction

from sample.models import Sample
from kmer.partitions import PARTITIONS


class StringManager(models.Manager):
    """
    String Manager.

    Use raw sql to insert strings into a temporary table, then only
    insert those rows that don't exist in the string table.
    """

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def bulk_create_new(self, recs):
        """
        Bulk insert.

        bulk create recs, skipping key conflicts that would raise an
        IntegrityError return value: int count of recs written
        """
        if not recs:
            return 0

        new_kmers = 0
        with transaction.atomic():
            cursor = connection.cursor()
            # write to kmer_string table
            values = ["('{0}')".format(k) for k in recs]
            for chunk in self.chunks(values, 100000):
                sql = """INSERT INTO kmer_stringtmp (string)
                         VALUES {0}
                         ON CONFLICT DO NOTHING;""".format(','.join(chunk))
                cursor.execute(sql)
                try:
                    # statusmessage is of form 'INSERT 0 1'
                    new_kmers += int(cursor.statusmessage.split(' ').pop())
                except (IndexError, ValueError):
                    raise Exception("Unexpected statusmessage from INSERT")
        return new_kmers

    def insert_into_partitions(self, recs, partition=None):
        """
        Insert directly to partitions.

        Group strings based on final 7 characters and insert directly to the
        partition table. Assumes the string does not already exist in the
        database.
        """
        if not recs:
            return 0

        partition_recs = {}
        for rec in recs:
            parent = PARTITIONS[rec[-7:]]
            if parent not in partition_recs:
                partition_recs[parent] = [rec]
            else:
                partition_recs[parent].append(rec)

        new_kmers = 0
        with transaction.atomic():
            cursor = connection.cursor()

            for parent, children in partition_recs.iteritems():
                # write directly to partition table
                table = 'kmer_string_{0}'.format(parent.lower())
                values = ["('{0}')".format(k) for k in children]
                for chunk in self.chunks(values, 100000):
                    sql = """INSERT INTO {0} (string)
                             VALUES {1}
                             ON CONFLICT DO NOTHING;""".format(
                        table, ','.join(chunk)
                    )
                    cursor.execute(sql)
                    try:
                        # statusmessage is of form 'INSERT 0 1'
                        new_kmers += int(cursor.statusmessage.split(' ').pop())
                    except (IndexError, ValueError):
                        raise Exception("Unexpected statusmessage from INSERT")
        return new_kmers


    def insert_into_partition(self, recs, partition):
        """
        Insert directly to a specific partition.

        Group strings based on final 7 characters and insert directly to the
        given partition table. Assumes the string does not already exist in the
        database.
        """
        if not recs:
            return 0

        new_kmers = 0
        with transaction.atomic():
            cursor = connection.cursor()
            table = 'kmer_string_{0}'.format(partition.lower())
            values = ["('{0}')".format(k) for k in recs]
            for chunk in self.chunks(values, 100000):
                sql = """INSERT INTO {0} (string)
                         VALUES {1}
                         ON CONFLICT DO NOTHING;""".format(
                    table, ','.join(chunk)
                )
                cursor.execute(sql)
                try:
                    # statusmessage is of form 'INSERT 0 1'
                    new_kmers += int(cursor.statusmessage.split(' ').pop())
                except (IndexError, ValueError):
                    raise Exception("Unexpected statusmessage from INSERT")
        return new_kmers

    def select_from_partitions(self, recs):
        """
        Select directly from partitions.

        Group strings based on final 7 characters and select directly to the
        partition table. Assumes the string already exists in the database.
        """
        if not recs:
            return 0

        partition_recs = {}
        for rec in recs:
            parent = PARTITIONS[rec[-7:]]
            if parent not in partition_recs:
                partition_recs[parent] = [rec]
            else:
                partition_recs[parent].append(rec)

        kmers = {}
        total = 1
        with transaction.atomic():
            cursor = connection.cursor()

            for parent, children in partition_recs.iteritems():
                # write directly to partition table
                table = 'kmer_string_{0}'.format(parent.lower())
                values = ["('{0}')".format(k) for k in children]
                run_time = time.time()

                for chunk in self.chunks(values, 10000):
                    sql = """SELECT id, string
                             FROM {0}
                             WHERE string IN ({1});""".format(
                        table,
                        ','.join(chunk)
                    )
                    cursor.execute(sql)
                    row_time = time.time()
                    for row in cursor:
                        kmers[row[1]] = row[0]
                print(('Table kmer_string_{0} ({1} of 512), Total Kmers: {2}, '
                       'Total Time: {3}s, Row Time: {4}s').format(
                    parent.lower(),
                    total,
                    len(children),
                    float(time.time() - run_time),
                    float(time.time() - row_time)
                ))
                total += 1
        return kmers


class FixedCharField(models.Field):
    """Force creation of a CHAR field not VARCHAR."""

    def __init__(self, max_length, *args, **kwargs):
        """Initialize."""
        self.max_length = max_length
        super(FixedCharField, self).__init__(
            max_length=max_length, *args, **kwargs
        )

    def db_type(self, connection):
        """Explicit char."""
        return 'char(%s)' % self.max_length


class StringBase(models.Model):
    """Unique 31-mer strings stored as strings."""

    string = FixedCharField(max_length=31, unique=True)

    class Meta:
        abstract = True


class StringTmp(StringBase):
    """Temporary table to check for existing kmers."""

    pass


class String(StringBase):
    """Unique 31-mer strings stored as strings."""

    objects = StringManager()


# Create partition every 20 million records
@architect.install('partition', type='range', subtype='integer',
                   constraint='20000000', column='id')
class Count(models.Model):
    """Kmer counts from each sample."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    string_id = models.PositiveIntegerField()
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('sample', 'string_id')


class Total(models.Model):
    """Total kmer counts from each sample."""

    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    singletons = models.PositiveIntegerField()
