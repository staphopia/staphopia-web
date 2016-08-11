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
import glob

from django.db import transaction
from django.core.management.base import CommandError

from kmer.models import Total
from staphopia.utils import timeit

CHUNK_SIZE = 1000000
INDEX_NAME = "kmers"
TYPE_NAME = "kmer"
HOST = "staphopia.genetics.emory.edu:9200"
ES_HOST = "http://staphopia.genetics.emory.edu:9200/kmers/kmer/_bulk"
SCRIPT = ("if (!ctx._source.samples.contains(s)){"
          "ctx._source.samples.add(s); ctx._source.count += 1;}")

BULK_SCRIPT = ("for(var i=0; i < sample.length; i++){"
               "if (!ctx._source.samples.contains(sample[i])){"
               "ctx._source.samples.add(sample[i]); ctx._source.count += 1;}}")


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def format_sample_pk(pk):
    """Format a sample primary key for elasticsearch."""
    return '{0}'.format(str(pk).zfill(8))


def get_samples(project_dir):
    """Return sample directories of a given project directory."""
    samples = {}
    for root, dirs, files in os.walk(project_dir):
        for d in dirs:
            path = '{0}/{1}'.format(root, d)
            try:
                samples[d] = {
                    'fq': glob.glob('{0}/*.cleanup.fastq.gz'.format(path))[0],
                    'jf': glob.glob('{0}/analyses/kmer/*.jf'.format(path))[0]
                }
            except IndexError:
                raise CommandError((
                    'Verify all samples in your project directory have been '
                    'run. Culprit is {0}'.format(path)
                ))
        break

    return samples


@timeit
def jellyfish_dump(jf):
    """Get kmer counts from a given jellyfish database."""
    cmd = ['jellyfish', 'dump', '-c', jf]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.split('\n')


@timeit
def insert_data_chunk(data_chunk, host=ES_HOST):
    """Send data to elasticsearch."""
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    try:
        for i in data_chunk:
            tmp.write('{0}\n'.format(json.dumps(i)))
    finally:
        tmp.close()
        res = requests.post(host, data=file(path, 'rb').read())
        text = res.json()
        print('\t\t{0} kmers loaded, (errors: {1}, took: {2}ms)'.format(
            len(text['items']), text['errors'], text['took']
        ))
        os.remove(path)
    return True


@transaction.atomic
def insert_kmer_stats(sample, total, singletons):
    """Insert kmer stats to the database."""
    Total.objects.get_or_create(
        sample=sample,
        total=total,
        singletons=singletons
    )

    print("{0}: Inserted {1} kmers ({2} are singletons)".format(
        sample.db_tag, total, singletons
    ))


@timeit
def insert_in_bulk(jf, partition):
    """Insert kmer counts into the database."""
    kmers = {}
    print("\t\tReading kmers...")
    with open(jf, 'r') as fh:
        for line in fh:
            kmer, sample = line.rstrip().split('\t')
            if kmer not in kmers:
                kmers[kmer] = [sample]
            else:
                kmers[kmer].append(sample)

    # Create necessary JSON for BULK insert
    bulk_data = []
    print("\t\tProcessing kmers for bulk insert...")
    for k, v in kmers.iteritems():
        bulk_data.append({"update": {"_retry_on_conflict": 5, "_id": k}})
        bulk_data.append({
            "script": {
                "inline": BULK_SCRIPT,
                "lang": "javascript",
                "params": {"sample": v}
            },
            "upsert": {"count": len(v), "samples": v}
        })

    # Insert the totals
    print("\t\tBeginning bulk insert, may take a while...")
    host = "http://{0}/kmer_{1}/kmer/_bulk".format(HOST, partition.lower())
    for chunk in chunks(bulk_data, CHUNK_SIZE):
        insert_data_chunk(chunk, host=host)


def insert_kmer_counts(jf, sample):
    """Insert kmer counts into the database."""
    start_time = time.time()
    jf_dump = jellyfish_dump(jf)
    bulk_data = []
    sample_id = format_sample_pk(sample.pk)
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
