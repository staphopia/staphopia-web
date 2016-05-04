"""
Useful functions associated with kmers.

To use:
from kmer.tools import UTIL1, UTIL2, etc...
"""
import time

from django.db import transaction

from elasticsearch import Elasticsearch, client

from kmer.models import Total
from staphopia.utils import timeit

CHUNK_SIZE = 2500
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
def insert_data(es, type, bulk_data):
    """Send data to elasticsearch."""
    total_chunks = int(len(bulk_data) / float(CHUNK_SIZE))
    total = 0
    for chunk in chunks(bulk_data, CHUNK_SIZE):
        es.bulk(index=INDEX_NAME, doc_type=type, body=chunk, refresh=True)
        if total % 500 == 0:
            print('\tProcessed {0} of {1} chunks'.format(total, total_chunks))
        total += 1
    return True


@transaction.atomic
def insert_kmer_counts(jf, sample):
    """Insert kmer counts into the database."""
    es = Elasticsearch(hosts=[ES_HOST])
    start_time = time.time()
    jf_dump = jellyfish_dump(jf)
    bulk_data = []
    sample_id = '{0}'.format(str(sample.pk).zfill(8))
    sample
    singletons = 0
    total = 0

    sample_script = (
        'if (!ctx._source.samples.contains(sample))'
        '{ctx._source.samples.add(sample); ctx._source.count += 1;}'
    )

    for line in jf_dump:
        if not line:
            continue
        kmer, count = line.rstrip().split()
        count = int(count)
        total += 1
        sample_name = '{0}-{1}'.format(sample_id, count)
        bulk_data.append(
            { "update" : { "_id" : kmer, "_type": "kmer", "_index":"kmers","_retry_on_conflict" : 3} }
        )

        bulk_data.append({
            "script": {
                "inline": sample_script,
                "lang": "javascript",
                "params": {
                    "sample": sample_name
                }
            },
            "upsert": {
                "count": 1,
                "samples" : [sample_name]
            }
        })

        if count == 1:
            singletons += 1

        if total % 1000000 == 0:
            print('\tProcessed {0} of {1} kmers'.format(total, len(jf_dump)))

    # Insert the totals
    print("\tBeginning bulk insert, may take a while...")
    insert_data(es, "kmer", bulk_data)
    idx = client.IndicesClient(es)
    idx.refresh("kmers")

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
