"""
Useful functions used thoughout the project.

To use:
from staphopia.utils import UTIL1, UTIL2, etc...
"""
import gzip
import json
import os.path

from django.core.management.base import CommandError

from staphopia.models import BlastQuery


def timeit(method):
    """Return total runtime (in seconds) of a given method."""
    import time

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('{0}\t{1:.2f} sec'.format(method.__name__, te - ts))
        return result

    return timed


def md5sum(fname):
    """Get md5sum of a file."""
    from subprocess import Popen, PIPE
    f = Popen(['md5sum', fname], stdout=PIPE)
    stdout, stderr = f.communicate()

    return stdout.split()[0]


def jf_query(jf, fasta):
    """Get md5sum of a file."""
    from subprocess import Popen, PIPE
    f = Popen(['jellyfish', 'query', jf, '-s', fasta], stdout=PIPE)
    stdout, stderr = f.communicate()

    return stdout


def byte_to_string(b):
    if b:
        return b.decode("utf-8")
    else:
        return ''


def gziplines(fname):
    """Use zcat to deliver lines from gzipped input."""
    from subprocess import Popen, PIPE
    f = Popen(['zcat', fname], stdout=PIPE)
    for line in f.stdout:
        yield byte_to_string(line)


def file_exists(input):
    """Test to make sure the file exists."""
    if os.path.exists(input):
        return True
    else:
        raise CommandError('{0} does not exist'.format(input))


def get_blast_query(title, length):
    """Get a query id for a given title and length."""
    query, created = BlastQuery.objects.get_or_create(
        title=title, length=length
    )
    if created:
        print("Added {0} to BlastQuery table".format(title))

    return query


def read_json(json_file, compressed=False):
    """Return data imported from JSON file."""
    if file_exists(json_file):
        try:
            if compressed:
                with gzip.open(json_file, "rb") as f:
                    json_data = json.loads(f.read().decode("ascii"))
            else:
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
        except ValueError:
            raise CommandError('{0}: invalid JSON'.format(json_file))

        return json_data


def read_fasta(fasta, compressed=False):
    """Return a list of seqeunces from a given FASTA file."""
    if file_exists(fasta):
        id = None
        seq = []
        records = {}
        fh = None

        if compressed:
            fh = gziplines(fasta)
        else:
            fh = open(fasta, 'r')

        for line in fh:
            line = line.rstrip()
            if line.startswith('>'):
                if len(seq):
                    records[id] = ''.join(seq)
                    seq = []
                id = line[1:].split(' ')[0]
            else:
                seq.append(line)

        records[id] = ''.join(seq)

        return records


class REMatcher(object):
    """Simple RegEx matching function."""

    def __init__(self, matchstring):
        """Init, nothing special."""
        self.matchstring = matchstring

    def match(self, regexp):
        """Test the regex."""
        import re
        self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, i):
        """Retuen a list of the regex matches."""
        return self.rematch.group(i)


def reverse_complement(seq):
    """Reverse complement a DNA sequence."""
    complement = {
        'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
        'a': 't', 't': 'a', 'g': 'c', 'c': 'g'
    }
    return ''.join([complement[b] for b in seq[::-1]])
