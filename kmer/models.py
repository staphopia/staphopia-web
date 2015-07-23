import psycopg2

from django.db import models, connection, transaction

from samples.models import Sample
from analysis.models import PipelineVersion


class Kmer(models.Model):

    """ A linking table for Sample and Kmers. """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(PipelineVersion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sample', 'version')


class KmerString(models.Model):

    """ Unique 31-mer strings. """

    string = models.CharField(default='', max_length=31, unique=True,
                              db_index=True)


class KmerBinaryManager(models.Manager):

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l. """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def bulk_create_new(self, recs):
        """
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
            LOCK TABLE kmer_kmerbinarytmp IN EXCLUSIVE MODE;
            TRUNCATE TABLE kmer_kmerbinarytmp RESTART IDENTITY;
            """
            cursor.execute(sql)

            # write to tmp table
            values = ['({0})'.format(psycopg2.Binary(k)) for k in recs]
            for chunk in self.chunks(values, 1000000):
                sql = "INSERT INTO kmer_kmerbinarytmp (string) VALUES {0};".format(','.join(chunk))
                cursor.execute(sql)

            sql = """
            BEGIN;
            LOCK TABLE kmer_kmerbinary IN EXCLUSIVE MODE;
            SELECT setval('kmer_kmerbinary_id_seq',
                          (SELECT MAX(id) FROM "kmer_kmerbinary"));
            INSERT INTO kmer_kmerbinary (string)
                SELECT string
                FROM kmer_kmerbinarytmp
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM kmer_kmerbinary
                    WHERE kmer_kmerbinarytmp.string = kmer_kmerbinary.string
                );
            """
            cursor.execute(sql)
            try:
                # statusmessage is of form 'INSERT 0 1'
                return int(cursor.statusmessage.split(' ').pop())
            except (IndexError, ValueError):
                raise Exception("Unexpected statusmessage from INSERT")


class KmerBinaryBase(models.Model):

    """ Unique 31-mer strings stored as binary. """

    string = models.BinaryField(max_length=8, unique=True, db_index=True)

    class Meta:
        abstract = True


class KmerBinaryTmp(KmerBinaryBase):
    pass


class KmerBinary(KmerBinaryBase):
    objects = KmerBinaryManager()

    def __unicode__(self):
        return "KmerBinary({})".format(self.string)


class KmerCount(models.Model):

    """ Kmer counts from each sample. """

    kmer = models.ForeignKey('Kmer', on_delete=models.CASCADE)
    string = models.ForeignKey('KmerBinary', on_delete=models.CASCADE)
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('kmer', 'string')


class KmerTotal(models.Model):

    """ Total kmer counts from each sample. """

    kmer = models.ForeignKey('Kmer', on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    singletons = models.PositiveIntegerField()
    new_kmers = models.PositiveIntegerField()
    runtime = models.PositiveIntegerField(default=0)
