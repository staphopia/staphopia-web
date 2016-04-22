"""
Useful functions associated with kmers.

To use:
from kmer.tools import UTIL1, UTIL2, etc...
"""
import time

from django.db import connection, transaction

from kmer.models import Count, Total, String
from staphopia.utils import timeit

def empty_table():
    """Empty Table and Reset id counters to 1."""
    print("Emptying kmer_string...")
    query = "TRUNCATE TABLE kmer_string RESTART IDENTITY CASCADE;"
    cursor = connection.cursor()
    cursor.execute(query)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

@timeit
def jellyfish_dump(jf):
    """Get kmer counts from a given jellyfish database."""
    import subprocess
    cmd = ['jellyfish', 'dump', '-c', jf]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.split('\n')

@timeit
def insert_strings(kmers):
    """Insert kmer strings into the database."""
    print("\tInserting strings to database... might be a while...")
    return String.objects.insert_into_partitions(kmers)

@timeit
def get_string_ids(kmers):
    """select kmer strings from the database."""
    print("\tPulling string ids from database... might be a while...")
    return String.objects.select_from_partitions(kmers)


@transaction.atomic
@timeit
def insert_counts(ids, counts, kmers, sample):
    """Insert kmer counts into the database."""
    print("\tInserting kmer counts... might be a while...")
    new_counts = 0
    with transaction.atomic():
        cursor = connection.cursor()
        # write to kmer_string table
        values = [
            "({0}, {1}, {2})".format(sample.pk, ids[k], counts[k])
            for k in kmers
        ]
        for chunk in chunks(values, 10000):
            sql = """INSERT INTO kmer_count (sample_id, string_id, count)
                     VALUES {0}
                     ON CONFLICT DO NOTHING;""".format(','.join(chunk))
            cursor.execute(sql)
            try:
                # statusmessage is of form 'INSERT 0 1'
                new_counts += int(cursor.statusmessage.split(' ').pop())
            except (IndexError, ValueError):
                raise Exception("Unexpected statusmessage from INSERT")
    return new_counts

def insert_kmer_counts(jf, sample, force=False):
    """Insert kmer counts into the database."""
    if force:
        print("\tForce used, emptying Kmer related results.")
        Count.objects.filter(sample=sample).delete()
        Total.objects.filter(sample=sample).delete()

    start_time = time.time()
    jf_dump = jellyfish_dump(jf)
    counts = {}
    kmers = []
    singletons = 0
    for line in jf_dump:
        if not line:
            continue
        kmer, count = line.rstrip().split()
        counts[kmer] = int(count)
        kmers.append(kmer)

        if int(count) == 1:
            singletons += 1

    # Get kmers that exist
    existing_ids = get_string_ids(kmers)

    # Take the kmers that aren't already in the databse and insert them
    new_kmers = list(set(kmers).difference(set(existing_ids.keys())))
    new_kmer_count = 0
    if len(new_kmers):
        new_kmer_count = insert_strings(new_kmers)
        kmer_ids = get_string_ids(new_kmers)
        for k,v in kmer_ids.items():
            existing_ids[k] = v

    # Insert the counts
    new_counts = insert_counts(existing_ids, counts, kmers, sample)

    # Insert the totals
    runtime = int(time.time() - start_time)
    Total.objects.create(
        sample=sample,
        total=len(jf_dump),
        singletons=singletons,
        new_kmers=len(new_kmers),
        runtime=runtime
    )

    print("Total kmers: {0}".format(len(jf_dump)))
    print("Total singletons: {0}".format(singletons))
    print("Total New k-mers: {0} ({1})".format(len(new_kmers), new_kmer_count))
    print("Total New Counts: {0}".format(new_counts))
    print("Total Runtime: {0}".format(runtime))

