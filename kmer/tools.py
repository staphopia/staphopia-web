"""
Useful functions associated with kmers.

To use:
from kmer.tools import UTIL1, UTIL2, etc...
"""
import subprocess
import requests
import tempfile
import time
import json
import os

from django.db import transaction

from kmer.models import Total
from staphopia.utils import timeit

CHUNK_SIZE = 2000000
INDEX_NAME = "kmers"
TYPE_NAME = "kmer"
ES_HOST = "http://staphopia.genetics.emory.edu:9200/kmers/kmer/_bulk"
SCRIPT = ("if (!ctx._source.samples.contains(s)){"
          "ctx._source.samples.add(s); ctx._source.count += 1;}")


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


@timeit
def jellyfish_dump(jf):
    """Get kmer counts from a given jellyfish database."""
    cmd = ['jellyfish', 'dump', '-c', jf]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.split('\n')


@timeit
def insert_data_chunk(data_chunk):
    """Send data to elasticsearch."""
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    try:
        for i in data_chunk:
            tmp.write('{0}\n'.format(json.dumps(i)))
    finally:
        tmp.close()
        res = requests.post(ES_HOST, data=file(path, 'rb').read())
        text = res.json()
        print('{0} kmers loader, (errors: {1}, took: {2}ms)'.format(
            len(text['items']), text['errors'], text['took']
        ))
        os.remove(path)
    return True


@transaction.atomic
def insert_kmer_stats(sample, total, singletons, runtime):
    """Insert kmer stats to the database."""
    Total.objects.get_or_create(
        sample=sample,
        total=total,
        singletons=singletons,
        runtime=runtime
    )

    print("Total kmers: {0}".format(total))
    print("Total singletons: {0}".format(singletons))
    print("Total Runtime: {0}".format(runtime))


def format_kmer_counts(jf, sample, outdir):
    """Insert kmer counts into the database."""
    start_time = time.time()
    jf_dump = jellyfish_dump(jf)
    total_kmers = len(jf_dump) - 1
    total = 0
    data = {"total": total_kmers, "singletons": 0, "kmers": []}

    for line in jf_dump:
        if not line:
            continue
        kmer, count = line.rstrip().split()
        count = int(count)
        total += 1
        data['kmers'].append({"string":kmer, "count":count})
        if count == 1:
            data['singletons'] += 1

        if total % 1000000 == 0:
            print('\tProcessed {0} of {1} kmers'.format(total, total_kmers))

    # Insert the totals
    print("\tFormatting kmers for bulk insert...")
    sid = '{0}'.format(str(sample.pk).zfill(8))
    create = {"index": {"_index":"kmers_nested", "_type":"sample", "_id":sid}}
    with open('{0}/{1}.json'.format(outdir, sid), 'w') as fh:
        fh.write("{0}\n".format(json.dumps(create, separators=(',',':'))))
        fh.write("{0}\n".format(json.dumps(data, separators=(',',':'))))

    runtime = int(time.time() - start_time)
    insert_kmer_stats(sample, data['total'], data['singletons'], runtime)



def insert_kmer_counts(jf, sample):
    """Insert kmer counts into the database."""
    start_time = time.time()
    jf_dump = jellyfish_dump(jf)
    bulk_data = []
    sample_id = '{0}'.format(str(sample.pk).zfill(8))
    singletons = 0
    total = 0

    for line in jf_dump:
        if not line:
            continue
        kmer, count = line.rstrip().split()
        count = int(count)
        total += 1
        sample_name = '{0}-{1}'.format(sample_id, count)
        bulk_data.append({
            "update": {
                "_retry_on_conflict": 5,
                "_id": kmer
            }
        })
        bulk_data.append({
            "script": {
                "inline": SCRIPT,
                "lang": "javascript",
                "params": {"s": sample_name}
            },
            "upsert": {"count": 1, "samples": [sample_name]}
        })
        if count == 1:
            singletons += 1

        if total % 1000000 == 0:
            print('\tProcessed {0} of {1} kmers'.format(total, len(jf_dump)))

    # Insert the totals
    print("\tBeginning bulk insert, may take a while...")
    for chunk in chunks(bulk_data, CHUNK_SIZE):
        insert_data_chunk(chunk)

    runtime = int(time.time() - start_time)
    insert_kmer_stats(sample, len(jf_dump), singletons, runtime)
