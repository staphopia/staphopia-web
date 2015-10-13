"""
Kmer Application Models.

These are models to store information on the Kmer analysis of Staphopia
samples.
"""
import architect
import psycopg2

from django.db import models, connection, transaction

from sample.models import MetaData


class BinaryManager(models.Manager):

    """
    Binary Manager.

    Use raw sql to insert binary strings into a temporary table, then only
    insert those rows that don't exist in the binary table.
    """

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l. """
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

        with transaction.atomic():
            cursor = connection.cursor()

            # lock and empty tmp table
            sql = """
            BEGIN;
            LOCK TABLE kmer_binarytmp IN EXCLUSIVE MODE;
            TRUNCATE TABLE kmer_binarytmp RESTART IDENTITY;
            """
            cursor.execute(sql)

            # write to tmp table
            values = ['({0})'.format(psycopg2.Binary(k)) for k in recs]
            for chunk in self.chunks(values, 100000):
                sql = """INSERT INTO kmer_binarytmp (string)
                         VALUES {0};""".format(','.join(chunk))
                cursor.execute(sql)

            sql = """
            BEGIN;
            LOCK TABLE kmer_binary IN EXCLUSIVE MODE;
            SELECT setval('kmer_binary_id_seq',
                          (SELECT MAX(id) FROM "kmer_binary"));
            INSERT INTO kmer_binary (string)
                SELECT string
                FROM kmer_binarytmp
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM kmer_binary
                    WHERE kmer_binarytmp.string = kmer_binary.string
                );
            """
            cursor.execute(sql)
            try:
                # statusmessage is of form 'INSERT 0 1'
                return int(cursor.statusmessage.split(' ').pop())
            except (IndexError, ValueError):
                raise Exception("Unexpected statusmessage from INSERT")


class BinaryBase(models.Model):

    """ Unique 31-mer strings stored as binary. """

    string = models.BinaryField(max_length=8, unique=True)

    class Meta:
        abstract = True


class BinaryTemporary(models.Model):

    """ Unique 31-mer strings stored as binary. """

    string = models.BinaryField(max_length=8)


class BinaryTmp(BinaryBase):

    """ Temporary table to check for existing kmers. """

    pass


# Create partition every 20 million records
@architect.install('partition', type='range', subtype='integer',
                   constraint='20000000', column='id')
class Binary(BinaryBase):

    """ Binary table manager. """

    objects = BinaryManager()

    def __unicode__(self):
        """ Return binary string. """
        return "Binary({})".format(self.string)


# Create partition every 20 million records
@architect.install('partition', type='range', subtype='integer',
                   constraint='20000000', column='id')
class Count(models.Model):

    """ Kmer counts from each sample. """

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    string = models.ForeignKey('Binary', on_delete=models.CASCADE)
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('sample', 'string')


class Total(models.Model):

    """ Total kmer counts from each sample. """

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    singletons = models.PositiveIntegerField()
    new_kmers = models.PositiveIntegerField()
    runtime = models.PositiveIntegerField(default=0)
