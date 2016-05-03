"""
Useful functions associated with kmers.

To use:
from kmer.tools import UTIL1, UTIL2, etc...
"""
import time

from django.db import transaction

from elasticsearch import Elasticsearch, IndicesClient

from kmer.models import Total
from staphopia.utils import timeit

INDEX_NAME = "kmers"
ES_HOST = "loma.genetics.emory.edu"


@timeit
def jellyfish_dump(jf):
    """Get kmer counts from a given jellyfish database."""
    import subprocess
    cmd = ['jellyfish', 'dump', '-c', jf]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.split('\n')


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


@timeit
def insert_data(es, bulk_data):
    """Send data to elasticsearch."""
    for chunk in chunks(bulk_data, 10000):
        es.bulk(index=INDEX_NAME, body=chunk, refresh=True)
    return True


@transaction.atomic
def insert_kmer_counts(jf, sample):
    """Insert kmer counts into the database."""
    es = Elasticsearch(hosts=[ES_HOST])
    start_time = time.time()
    jf_dump = jellyfish_dump(jf)
    kmer_data = []
    sample_data = []
    singletons = 0
    total = 0
    for line in jf_dump:
        if not line:
            continue
        kmer, count = line.rstrip().split()
        count = int(count)
        total += 1
        kmer_data.append({
            "index": {"_index": INDEX_NAME, "_type": "kmer", "_id": kmer}
        })
        sample_data.append({
            "index": {
                "_index": INDEX_NAME,
                "_type": "sample",
                "_parent": kmer,
                "_id": '{0}_{1}'.format(sample.pk, kmer)
            }
        })
        sample_data.append({
            "sample_id": sample.pk,
            "count": count
        })

        if count == 1:
            singletons += 1

    # Bulk insert k-mers and counts
    print("Beginning bulk insert, may take a while...")
    insert_data(es, kmer_data)
    insert_data(es, sample_data)

    # Insert the totals
    runtime = int(time.time() - start_time)
    Total.objects.get_or_create(
        sample=sample,
        total=len(jf_dump),
        singletons=singletons,
        runtime=runtime
    )

    print("Total kmers: {0}".format(total))
    print("Total singletons: {0}".format(singletons))
    print("Total Runtime: {0}".format(runtime))
