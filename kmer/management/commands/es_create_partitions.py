"""Create Elasticsearch indicies for partions."""
import requests
import time

from django.core.management.base import BaseCommand

from kmer.partitions import PARTITIONS

ES_HOST = 'staphopia.emory.edu:9200'
INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 5,
        "number_of_replicas": 1
    },
    "mappings": {
        "kmer": {
            "_all": {"enabled": False},
            "properties": {
                "count": {"type": "long"},
                "samples": {"type": "string"}
            }
        }
    },
    "aliases": {"kmers": {}}
}


class Command(BaseCommand):
    """Create Elasticsearch indicies for partions."""

    help = 'Create Elasticsearch indicies for partions.'

    def handle(self, *args, **opts):
        """Create partitions."""
        parents = {}
        for child, parent in PARTITIONS.items():
            parents[parent] = True

        current = 1
        total = len(parents.keys())
        for parent in parents.keys():
            print("{0} of {1}, Response: {2}".format(
                current, total,
                self.create_partition(parent)
            ))
            time.sleep(1)
            current += 1

    def create_partition(self, partition):
        """Send data to elasticsearch."""
        index = "http://{0}/kmer_{1}".format(ES_HOST, partition.lower())
        res = requests.post(index, json=INDEX_MAPPING)
        return res.text
